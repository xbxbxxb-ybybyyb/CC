import pandas as pd
from tqdm import tqdm
from xquant.factordata import FactorData
s = FactorData()

start_date, end_date =  20160101, 20250331
end_date_next = int(s.tradingday(end_date,2)[-1])
trading_days = s.tradingday(start_date, end_date_next)

index_minute_data_path = '/data/group/800080/warehouseJG/prod/LOCAL_DATA/CSV/WIND/MINUTE/index_perdate/'

index_minute_close_all = []
for date in tqdm(trading_days):
    minute_df = pd.read_pickle(index_minute_data_path + date + '.pkl', compression='gzip')
    minute_df = minute_df.reset_index()
    minute_df['dt'] = pd.to_datetime(minute_df['dt'].astype(str))
    minute_df = minute_df[minute_df['Ticker']==852]
    minute_df['Ticker'] = '000852.SH'
    minute_close_df = minute_df.set_index(['dt', 'Ticker', 'minute'])['close'].unstack(level=-1)
    index_minute_close_all.append(minute_close_df)

minute_close_df_all = pd.concat(index_minute_close_all)

open_time_dict = {
    '1430_1440_twap':[1430,1431,1432,1433,1434,1435,1436,1437,1438,1439]
}

close_time_dict = {
    '0930_0940_twap':[930,931,932,933,934,935,936,937,938,939]
}
cols = []
for open_time in open_time_dict.keys():
    for close_time in close_time_dict.keys():
        minute_close_df_all[close_time] = minute_close_df_all[close_time_dict[close_time]].mean(axis=1)
        minute_close_df_all['next_'+close_time] = minute_close_df_all.groupby('Ticker')[close_time].shift(-1)
        minute_close_df_all[open_time] = minute_close_df_all[open_time_dict[open_time]].mean(axis=1)
        minute_close_df_all['label_t2o10dc_long'] = minute_close_df_all['next_'+close_time] / minute_close_df_all[open_time] - 1
        minute_close_df_all['label_t2o10dc_short'] = 1 - minute_close_df_all['next_' + close_time] / minute_close_df_all[open_time]
        cols.append('label_t2o10dc_long')
        cols.append('label_t2o10dc_short')

minute_close_df_all = minute_close_df_all[cols].loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
minute_close_df_all.to_pickle('/dfs/user/023859/neptune/zz1000_index_label_%s_%s.pkl'%(start_date,end_date))

# 指数行情
# index_list = ['000852.SH']
# index_md = IO.read_data([start_date, end_date], universe=index_list, columns=['S_DQ_OPEN', 'S_DQ_CLOSE'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5')
# index_md = index_md.rename(columns={'S_DQ_OPEN': 'open', 'S_DQ_CLOSE': 'close'})
#
# for index in tqdm(index_md.index):
#     dt, code = index
#     date = dt.strftime('%Y%m%d')
#     tick_df = mdp.get_data_by_date('Index', code, date)
#     index_md.loc[index, 'close_check'] = tick_df['LastPx'].iloc[-1]
#
#     tick_df['MDTime'] = tick_df['MDTime'].astype(int)
#     tick_df = tick_df[(tick_df['MDTime'] > 93000000) & (tick_df['MDTime'] < 145700000)]
#     tick_df = tick_df[~((tick_df['MDTime'] > 113000000) & (tick_df['MDTime'] < 130000000))]
#     index_md.loc[index, 'twap'] = tick_df['LastPx'].mean()
#     index_md.loc[index, 'price_0931'] = tick_df[tick_df['MDTime'] >= 93100000]['LastPx'].iloc[0]
#
# index_md = index_md.sort_values(['Ticker', 'dt'])
# index_md.to_pickle('/data/user/023859/Hedging/index_price_%s_%s.pkl'%(start_date,end_date))
