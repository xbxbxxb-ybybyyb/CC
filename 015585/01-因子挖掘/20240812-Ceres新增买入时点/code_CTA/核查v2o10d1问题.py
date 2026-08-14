import IO
import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from joblib import Parallel, delayed
'''
1、931判断，最新价 > open 且 最新涨跌幅>-2%，则931买入
2、否则，对价格序列进行小波变换，剔除噪音后，在RSI(6)背离时、MACD背离时买入，取两者的首个时间点
'''
s = FactorData()
from xquant.marketdata import MarketData
import pywt
mdp = MarketData()
def add_time(start, adding):
    start_str = str(start)
    end_int = int(start_str[:~6]) * 3600000 + \
              int(start_str[~6:~4]) * 60000 + \
              int(start_str[~4:~2]) * 1000 + \
              int(start_str[~2:]) + adding
    end_time = int((end_int - np.floor(end_int / 1000) * 1000) + \
                   (np.floor(end_int / 1000) - np.floor(end_int / 60000) * 60) * 1000 + \
                   (np.floor(end_int / 60000) - np.floor(end_int / 3600000) * 60) * 100000 + \
                   (np.floor(end_int / 3600000)) * 10000000)
    if (start < 113000000) & (end_time > 113000000) & (end_time < 130000000):
        end_time = add_time(end_time, 5400000)
    if (start > 130000000) & (end_time < 130000000) & (end_time > 113000000):
        end_time = add_time(end_time, -5400000)
    return max(93000000, end_time)

#参数设置
start_date, end_date = 20160101, 20191231
df=IO.read_data([start_date,end_date],alt='/data/user/015585/01-因子挖掘/20240812-Ceres新增买入时点/file/Basic_closed_hf_finish_20160101_20191231.h5')
df['st_indicator']=pd.read_pickle('/data/group/800463/data/st_indicator.pkl')['st_indicator']
df['st_indicator']=df['st_indicator'].fillna(0)
print('读取样本：',len(df))

#统计情况
sample=df.copy()
error_list = []
index = (pd.Timestamp('20190521'),'300241.SZ')
# def get_trigger(index):
print(index)

dt,Ticker=index
date=dt.strftime('%Y%m%d')
pre_close=sample.loc[index,'pre_close']
T_day_first_ZT_Time = sample.loc[index,'T_day_first_ZT_Time']
T_day_first_DT_Time = sample.loc[index,'T_day_first_DT_Time']
if (Ticker[0] == '3') & (date >= '20200824'):
    ul_price = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
    dl_price = np.floor(pre_close * 100 * 0.8 + 0.5) / 100
else:
    ul_price = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
    dl_price = np.floor(pre_close * 100 * 0.9 + 0.5) / 100

#读取数据
tick_df = mdp.get_data_by_date('Stock', Ticker, date)
tick_df['MDTime']=tick_df['MDTime'].astype(int)
tick_df = tick_df[((tick_df['MDTime'] >= 92500000) & (tick_df['MDTime'] <= 113000000))
                       | ((tick_df['MDTime'] >= 130000000) & (tick_df['MDTime'] <= 150000000))]
tick_df = tick_df[tick_df['LastPx'] > 0] # qyh：新增了时间筛选和无效数据剔除
#
# 计算未来十分钟twap
s1_buy_begin_time = 93100000
buy_end_time = min(150000000, add_time(s1_buy_begin_time, 10 * 60 * 1000))
tick_buy = tick_df[tick_df['MDTime'] > s1_buy_begin_time]
tick_buy = tick_buy[tick_buy['MDTime'] < buy_end_time]
if not np.isnan(T_day_first_ZT_Time):
    tick_buy = tick_buy[tick_buy['MDTime'] < T_day_first_ZT_Time]
if not np.isnan(T_day_first_DT_Time):
    tick_buy = tick_buy[tick_buy['MDTime'] < T_day_first_DT_Time]
if len(tick_buy) > 0:
    T_s1_10_twap_before_ZT = tick_buy['LastPx'].mean()
else:
    T_s1_10_twap_before_ZT = np.nan

MD_data = IO.read_data([20190401, 20190630],
                       columns=['high','low','vwap','adjfactor']
                       , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
is_yzb = MD_data['low'] == MD_data['high']
MD_data.loc[is_yzb,'vwap']=np.nan
MD_data.loc[is_yzb,'adjfactor']=np.nan
sample['adjfactor']=MD_data['adjfactor']
sample['next_vwap']=MD_data['vwap'].unstack().fillna(method='bfill').shift(-1).stack()
sample['next_adjfactor']=MD_data['adjfactor'].unstack().fillna(method='bfill').shift(-1).stack()
sample['label_v2o10d1']=sample['next_vwap']*sample['next_adjfactor']/sample['T_s1_10_twap_before_ZT']/sample['adjfactor']-1
