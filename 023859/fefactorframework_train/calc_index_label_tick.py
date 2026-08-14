import pandas as pd
import os
import numpy as np
from xquant.factordata import FactorData
s = FactorData()

start_date, end_date = 20160101, 20250514
trading_days = s.tradingday(start_date, end_date)
index_df = pd.DataFrame(index=trading_days,columns=['1430_1440_twap','0930_0940_twap'])
for date in trading_days:
    tick_data = pd.read_pickle(f'/dfs/group/800463/data/index_data/ZZ1000/{date}'+'.pkl')
    tick_data_afternoon = tick_data[(tick_data['MDTime'] > 143000000)&(tick_data['MDTime'] < 144000000)]
    tick_data_morning = tick_data[(tick_data['MDTime'] > 93000000)&(tick_data['MDTime'] < 94000000)]
    twap_1430_1440 = tick_data_afternoon['LastPx'].mean()
    twap_0930_0940 = tick_data_morning['LastPx'].mean()
    index_df.loc[date,'1430_1440_twap'] = twap_1430_1440
    index_df.loc[date,'0930_0940_twap'] = twap_0930_0940

index_df['next_0930_0940_twap'] = index_df['0930_0940_twap'].shift(-1)
index_df['label_t2o10dc_neg'] = index_df['next_0930_0940_twap'] / index_df['1430_1440_twap'] - 1
index_df['label_t2o10dc_pos'] = -index_df['label_t2o10dc_neg']

index_df = index_df.rename_axis('dt')
index_df = index_df.reset_index()

index_df['dt'] = pd.to_datetime(index_df['dt'])
index_df['Ticker'] = '000852.SH'

index_df.set_index(['dt','Ticker'])[['label_t2o10dc_pos','label_t2o10dc_neg']].to_pickle(f'/dfs/user/023859/neptune/20250513/index_label_{start_date}_{end_date}.pkl')