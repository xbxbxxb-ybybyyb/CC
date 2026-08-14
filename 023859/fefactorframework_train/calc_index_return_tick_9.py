import pandas as pd
import os
import numpy as np
from xquant.factordata import FactorData
s = FactorData()

start_date, end_date = 20160101, 20241231
trading_days = s.tradingday(start_date, end_date)

period_dict = {
    '930_1000':[93000000,100000000],
    '1000_1030':[100000000,103000000],
    '1030_1100':[103000000,110000000],
    '1100_1130':[110000000,113000000],
    '1300_1330':[130000000,133000000],
    '1330_1400':[133000000,140000000],
    '1400_1430':[140000000,143000000],
    '1430_1500':[143000000,150000000],
}

index_df = pd.DataFrame(index=trading_days)
for date in trading_days:
    tick_data = pd.read_pickle(f'/dfs/group/800463/data/index_data/ZZ1000/{date}'+'.pkl')
    tick_data = tick_data[(tick_data['MDTime']>=93000000)]
    OpenPx = tick_data['OpenPx'].iloc[-1]
    PreClosePx = tick_data['PreClosePx'].iloc[-1]
    index_df.loc[date, 'preclose_open'] = OpenPx/PreClosePx - 1
    for period in period_dict:
        tick_data_period = tick_data[(tick_data['MDTime'] >= period_dict[period][0]) & (tick_data['MDTime'] <= period_dict[period][1])]
        if len(tick_data_period):
            index_df.loc[date, period] = tick_data_period['LastPx'].iloc[-1]/tick_data_period['LastPx'].iloc[0] - 1

index_df = index_df.rename_axis('dt')
index_df = index_df.reset_index()

index_df['dt'] = pd.to_datetime(index_df['dt'])
index_df['Ticker'] = '000852.SH'

index_df.set_index(['dt','Ticker']).to_pickle(f'/dfs/user/023859/neptune/20250526/index_label_period_{start_date}_{end_date}.pkl')