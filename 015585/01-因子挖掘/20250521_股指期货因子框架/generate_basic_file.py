import numpy as np
import pandas as pd
import IO
import numpy as np
from datetime import datetime, timedelta
from xquant.futuredata import FutureData
fd = FutureData()
from xquant.factordata import FactorData
s = FactorData()
'''
生成IM的BASIC_FILE
1、对时间段（2022-08-01~2025-04-30）内每个交易日，获取当月合约，获取当月合约的DELISTDATE，如若该日期在DELIST向前2个交易日或之后，改为次月合约
2、对每个DT，BASICFILE拓展为945到1430（闭区间），每隔30S的所有时点
'''

start_date = '20220801'
end_date = '20250430'
date_list = s.tradingday(int(start_date), int(end_date))

basic_file_future = pd.DataFrame()
def get_next_yearmonth(x): # x形如'2202'，返回'2203'
    year = x[0:2]
    month = x[2:4]
    month_next = int(month) + 1
    if month_next == 13:
        month_next = '01'
        year = str(int(year) + 1).zfill(2)
    else:
        month_next = str(month_next).zfill(2)
    return f'{year}{month_next}'

def extend_30s(basic_file_future, start_time = 93100000, end_time = 143000000, time_delta = 30):
    # 构造一个list，元素为MDTime，从start到end，间隔为time_delta
    start_time_ = datetime.strptime(f'{str(start_time).zfill(9)[0:2]}:{str(start_time).zfill(9)[2:4]}:{str(start_time).zfill(9)[4:6]}', '%H:%M:%S')
    end_time_ = datetime.strptime(f'{str(end_time).zfill(9)[0:2]}:{str(end_time).zfill(9)[2:4]}:{str(end_time).zfill(9)[4:6]}', '%H:%M:%S')
    time_list = []
    current_time = start_time_
    while current_time <= end_time_:
        time_str = f"{current_time.hour}{current_time.minute:02d}{current_time.second:02d}"
        time_list.append(time_str)
        current_time += timedelta(seconds=time_delta)
    time_list = [int(f'{x}000') for x in time_list]
    # time_list = [93100000, 100000000, 103000000, 110000000, 130000000, 133000000, 140000000, 143000000] # 按要求20250603改为8个时间点
    time_list = [x for x in time_list if not ((x > 113000000) and (x < 130000000))]
    # 拓展basic_file
    basic_file_future['time'] = np.nan
    basic_file_future['time'] = basic_file_future['time'].apply(lambda x : time_list)
    ##
    result_df = pd.DataFrame()
    basic_file_future = basic_file_future.reset_index()
    for index, row in basic_file_future.iterrows():
        print(row['dt'])
        elements = row['time']
        other_columns = {col: row[col] for col in basic_file_future.columns if col != 'time'}
        repeated_values = {col: [value] * len(elements) for col, value in other_columns.items()}
        temp_df = pd.DataFrame(repeated_values)
        temp_df['time'] = elements
        result_df = pd.concat([result_df, temp_df], ignore_index=True)
    result_df['dt'] = result_df['dt'].apply(lambda x : x.strftime('%Y%m%d')) + ' ' + result_df['time'].apply(lambda x : str(x).zfill(9))
    result_df['dt'] = result_df['dt'].apply(lambda x : pd.Timestamp(str(x[:-3])))
    used_columns = ['Future', 'FutureType', 'cctype', 'cdmonths',
       'cevalue', 'contract_id', 'ddate', 'delistdate', 'dlmonth', 'dmean',
       'dsite', 'exname', 'fspunit', 'ftmargins', 'listdate', 'lprice',
       'ltdated', 'ltdatehour', 'ltdldate', 'maxpricefluct', 'mfprice',
       'multiplier', 'name', 'poslimit', 'punit', 'rtd', 'sfullname', 'sname',
       'subtypcode', 'thours', 'tunit', 'type', 'udlsecode', 'time','date']
    result_df = result_df.set_index(['dt','Ticker'])[used_columns]
    result_df = result_df.sort_values(['dt','Ticker'])
    return result_df

for tradingday in date_list:
    print(tradingday)
    future_month = f'IM{tradingday[2:6]}.CF'
    df_future_basicinfo_date = fd.get_instrument_info(future_month).rename(columns = {'windcode':'Future','code':'FutureType',})
    df_future_basicinfo_date['Ticker'] = future_month # 先统一用当月的
    delist_date = df_future_basicinfo_date['delistdate'].values[0]
    delist_date_before2 = s.tradingday(int(delist_date), -2)[0] # 交割日的前1个交易日
    if tradingday >= delist_date_before2: # 交割日的前1个交易日之后的都用次月的
        future_month_next = f'IM{get_next_yearmonth(tradingday[2:6])}.CF'
        df_future_basicinfo_date = fd.get_instrument_info(future_month_next).rename(columns = {'windcode':'Future','code':'FutureType',})
        df_future_basicinfo_date['Ticker'] = future_month_next
    df_future_basicinfo_date['dt'] = pd.Timestamp(tradingday)
    df_future_basicinfo_date['date'] = tradingday
    df_future_basicinfo_date = df_future_basicinfo_date.set_index(['dt','Ticker'])
    basic_file_future = basic_file_future.append(df_future_basicinfo_date)
# 添加时分秒
print('添加时分秒信息')
basic_file_future = extend_30s(basic_file_future)

# 保存为h5 全集
out_path = f'/dfs/user/015585/00_股指期货策略/Basic_future_{start_date}_{end_date}.h5'
with pd.HDFStore(out_path) as h5_store:
    h5_store.put('data', basic_file_future, format='table', append=False, data_columns=True)
    h5_store.get_storer('data').attrs.modification_date = datetime.today()
# 保存为h5 样本内
out_path = f'/dfs/user/015585/00_股指期货策略/Basic_future_{20220801}_{20230731}.h5'
with pd.HDFStore(out_path) as h5_store:
    h5_store.put('data', basic_file_future.loc[pd.Timestamp('20220801'):pd.Timestamp('20230801')], format='table', append=False, data_columns=True) # 注意后延1天应对时分秒的情形
    h5_store.get_storer('data').attrs.modification_date = datetime.today()
# 保存为h5 样本外
out_path = f'/dfs/user/015585/00_股指期货策略/Basic_future_{20230801}_{20250430}.h5'
with pd.HDFStore(out_path) as h5_store:
    h5_store.put('data', basic_file_future.loc[pd.Timestamp('20230801'):pd.Timestamp('20250501')], format='table', append=False, data_columns=True)
    h5_store.get_storer('data').attrs.modification_date = datetime.today()

# sft_basic生成
sft_file = pd.read_hdf('/dfs/user/020412/团队分享/for_qyh/Basic_future_20220801_20250430_addlabel_20250606.h5')
sft_file = sft_file[['label']]
from datetime import datetime
## 全集
out_path = '/dfs/user/015585/00_股指期货策略/sft_basic_formal_20220801_20250430.h5'
with pd.HDFStore(out_path) as h5_store:
    h5_store.put('data', sft_file, format='table', append=False, data_columns=True)
    h5_store.get_storer('data').attrs.modification_date = datetime.today()
## 样本内
out_path = '/dfs/user/015585/00_股指期货策略/sft_basic_formal_20220801_20230731.h5'
with pd.HDFStore(out_path) as h5_store:
    h5_store.put('data', sft_file.loc[pd.Timestamp('20220801'):pd.Timestamp('20230801')], format='table', append=False, data_columns=True)
    h5_store.get_storer('data').attrs.modification_date = datetime.today()
## 样本外
out_path = '/dfs/user/015585/00_股指期货策略/sft_basic_formal_20230801_20250430.h5'
with pd.HDFStore(out_path) as h5_store:
    h5_store.put('data', sft_file.loc[pd.Timestamp('20230801'):pd.Timestamp('20250501')], format='table', append=False, data_columns=True)
    h5_store.get_storer('data').attrs.modification_date = datetime.today()
