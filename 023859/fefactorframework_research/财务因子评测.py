import pandas as pd
from h5data.IO import IO
import numpy as np
from xquant.factordata import FactorData
s = FactorData()

start_date = 20170110
end_date = 20211231
sft_basic_path = '/data/user/023859/factor_zooZZ/factor_lib/sft_basic_formal_931_20160101_20241231.h5'  # 这个文件里有label和所有因子
df = pd.read_hdf(sft_basic_path).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
# 财务因子
all_factor_inf = pd.read_excel('/data/user/023859/factor_zooZZ/all_factor_inf.xlsx')
all_factor_inf = all_factor_inf[all_factor_inf['factor_type'].str.contains('xdb_balancesheet|xdb_cashflow|xdb_income')]
for factor in list(all_factor_inf['factor_name']):
    try:
        df_factor = pd.read_hdf(f'/data/user/023859/factor_zooZZ/all_factor/931/{factor}/{factor}.h5')
        df[f'{factor}'] = df_factor[f'{factor}']
    except:
        continue

# 财报日期
'''
与xdb_财务数据一致，获取AShareBalanceSheet中的ANN_DT
以ANN_DT = 0520为例，实际发布时间为0519 15:00到0520凌晨，由于数据更新的时间限制，认为这份报告在0520晚间的数据更新获取，即T日为0521时才会用到该数据
由此，0521为受到影响的第一天，如若0521为非交易日，则顺延到第一个交易日
'''
df_ann = IO.read_data([20150101, end_date], columns = ['WIND_CODE','ANN_DT'], alt = '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareBalanceSheet/AShareBalanceSheet.h5')
df_ann = df_ann.reset_index()[['WIND_CODE','ANN_DT']].rename(columns={'WIND_CODE':'Ticker'})

ann_dt_list = list(set(df_ann['ANN_DT']))
ann_dt_list.sort()
print('length ann_dt_list:', len(ann_dt_list))
dic_ann_dt = {}
for ann_dt in ann_dt_list:
    dic_ann_dt[ann_dt] = s.tradingday(int((pd.Timestamp(str(int(ann_dt))) + pd.Timedelta(days=1)).strftime('%Y%m%d')),1)[0] if not np.isnan(ann_dt) else np.nan
print('dic_ann_dt 完成')
df_ann['dt'] = df_ann['ANN_DT'].apply(lambda x : dic_ann_dt[x] if not np.isnan(x) else np.nan)
df_ann['dt'] = df_ann['dt'].apply(pd.Timestamp)
df_ann['first_after_financedate'] = 1
df_ann = df_ann[['dt','Ticker','first_after_financedate']].drop_duplicates(keep='first') # 年报和一季报可能同一天，要去重否则无法匹配
df_ann = df_ann.set_index(['dt','Ticker'])
df['first_after_financedate'] = df_ann['first_after_financedate']
df['first_after_financedate'] = df['first_after_financedate'].fillna(0)

df.to_pickle('/dfs/user/023859/neptune/sft_finance.pkl')