import pandas as pd
import os
filter_df = pd.read_pickle('/data/user/015585/01-因子挖掘/20230703-暑期实习生数据准备/code/filter_df.pkl')
all_df = pd.read_pickle('/data/user/015585/01-因子挖掘/20230703-暑期实习生数据准备/code/low_frequency_all.pkl')
all_df['next_vwap'] = all_df['vwap'].unstack().shift(-1).stack()
all_df['next_adjfactor'] = all_df['adjfactor'].unstack().shift(-1).stack()
res = pd.DataFrame()
list_date = os.listdir('/data/user/015585/01-因子挖掘/20230703-暑期实习生数据准备/result/')
list_date.sort()
for file in list_date:
    if file.endswith('.pkl'):
        print(file)
        try:
            df = pd.read_pickle('/data/user/015585/01-因子挖掘/20230703-暑期实习生数据准备/result/' + file).groupby(['dt','Ticker']).nth([-1])['LastPx']
            res = pd.concat([res,df],axis=0)
        except:
            print('file error:',file)
res = pd.DataFrame(res)
res.columns = ['940']
res = res.reset_index()
res['dt'] = res['index'].apply(lambda x : x[0])
res['Ticker'] = res['index'].apply(lambda x : x[1])
res = res.set_index(['dt','Ticker'])[['940']]
tmp = pd.merge(res,all_df[['next_vwap','adjfactor','next_adjfactor']],left_index=True,right_index=True,how='left')
print(tmp['next_vwap'] * tmp['next_adjfactor'] / tmp['940'] / tmp['adjfactor'])

