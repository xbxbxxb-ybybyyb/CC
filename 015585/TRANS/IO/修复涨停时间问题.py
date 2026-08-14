import IO
import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from joblib import Parallel, delayed
# RSI(6)背离 + -3% + 放宽阈值
s = FactorData()
from xquant.marketdata import MarketData
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
df=IO.read_data([start_date,end_date],alt='/data/group/800463/data/project2_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5')
for Ticker in df.loc[pd.Timestamp('20170331')].index:
    dt = pd.Timestamp('20170331')
    if df.loc[(dt,Ticker),'T_day_first_ZT_Time'] == -3:
        date = dt.strftime('%Y%m%d')
        pre_close = df.loc[(dt,Ticker), 'pre_close']
        if (Ticker[0] == '3') & (date >= '20200824'):
            ul_price = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
            dl_price = np.floor(pre_close * 100 * 0.8 + 0.5) / 100
        else:
            ul_price = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
            dl_price = np.floor(pre_close * 100 * 0.9 + 0.5) / 100
        transaction_df = mdp.get_data_by_date("Transaction", Ticker, date)  # qyh：只用于错误的T_day_first_ZT_Time和T_first_trans_ZT
        T_day_first_ZT_Time = int(transaction_df[transaction_df['TradePrice'] >= ul_price]['MDTime'].min()) if transaction_df[transaction_df['TradePrice'] >= ul_price].shape[0] > 0 else np.nan
        T_first_trans_ZT = int(transaction_df[transaction_df['TradePrice'] > 0]['TradePrice'].iloc[0] >= ul_price)
        df.loc[(dt, Ticker), 'T_day_first_ZT_Time'] = T_day_first_ZT_Time
        df.loc[(dt, Ticker), 'T_first_trans_ZT'] = T_first_trans_ZT
        print(dt,Ticker,T_day_first_ZT_Time,T_first_trans_ZT)
df.to_pickle('/data/user/015585/01-因子挖掘/20240812-Ceres新增买入时点/file/Basic_closed_hf_finish_20160101_20191231_saturn_update.pkl')