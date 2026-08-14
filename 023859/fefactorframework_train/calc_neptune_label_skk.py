import sys
import numpy as np
import pandas as pd

sys.path.append("../")
from h5data.IO import IO

def load_md_data(start_date, end_date, columns=[]):
    md_data = IO.read_data([start_date, end_date], columns=columns,alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    return md_data

md_data = load_md_data(start_date=20250101, end_date=20250331, columns=['close', 'pre_close'])
data_file = "/data/user/021012/团队分享/for_tsq/neptune/p2_profit_intervalTwap_1430_1440_Sell_intervalTwap_930_940_0.10_0.10_20250101_20251231.h5"
data = pd.read_hdf(data_file)
data['close'] = md_data['close']
data['sell_vwap'] = (data['pct_T1']+1) * data['close']

data['pct_a'] = (data['pct_T'] + 1) * (data['pct_T1'] + 1) - 1
data['pct_T_a'] = data['close'] / data['buy_vwap'] - 1
data['pct_T1_a'] = data['sell_vwap'] / data['close'] - 1
data['pct_b'] = data['sell_vwap'] / data['buy_vwap'] - 1
ccc = data.loc[data['pct_a']!=data['pct']]
ddd = data.loc[data['pct_T_a']!=data['pct_T']]
eee = data.loc[(data['pct_T1_a']-data['pct_T1']).abs()>1e-12]
fff = data.loc[(data['pct_b']-data['pct']).abs()>1e-12]
print(3333333333, ccc[['pct_T', 'pct_T1', 'pct', 'pct_a']])
print(4444444444, ddd[['pct_T', 'pct_T_a', 'close', 'buy_vwap']])
print(5555555555, eee[['pct_T1', 'pct_T1_a', 'close', 'sell_vwap']])
print(6666666666, fff[['pct_b', 'pct', 'buy_vwap', 'sell_vwap']])
# print(1111111111, data[['pct_T', 'pct_T1', 'pct', 'close']])