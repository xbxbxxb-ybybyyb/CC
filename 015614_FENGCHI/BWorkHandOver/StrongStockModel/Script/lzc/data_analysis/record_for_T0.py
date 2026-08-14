# @Time : 2021/1/5 20:42
# @Author : Zhichen Lu
# @File : record_for_T0.py
import pandas as pd
import os
from multiprocessing import Pool,Manager

path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBasedVolConsiderV2/record/'
file_list = os.listdir(path)
list(filter(lambda x : '2019' in x,file_list))

out_path = path+'19_20_rev/'
if not os.path.exists(out_path):
    os.mkdir(out_path)
data = pd.read_pickle(path+'XGB_Linear_DTC_V2OutSample19_20Rev_deal_ratio_0.1_per_ratio_0.0050OutSample.pkl')
record = Manager().dict()
for each in data:
    record[each] = data[each]
record_list = Manager().list()

def get_record(stk):
    temp = data[stk]
    temp = temp[temp['flag'].isin(['B','S'])][['flag','vol','deal_price']].reset_index()
    temp['stk_id'] = str(stk).zfill(6)+'.SZ' if stk<400000 else str(stk)+'.SH'
    temp['vol'] = temp['vol'].apply(abs)
    record_list.append(temp)
    print(stk,'done')

pool = Pool(10)
pool.map(get_record,list(data.keys()))
pool.close()
pool.join()

pd.to_pickle(record_list._getvalue(),out_path+'res_list.pkl')
record_list = pd.read_pickle(out_path+'res_list.pkl')
record_df = pd.concat(record_list)

date_list = sorted(list(set(record_df['date'])))
record_df = record_df.sort_values(['date','time','stk_id'])

for date in date_list:
    temp = record_df[record_df['date'].eq(date)]
    temp.index = list(range(temp.shape[0]))
    temp.to_csv(out_path+'%d.csv'%date)
    print(date)