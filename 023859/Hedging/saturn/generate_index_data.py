import IO
import pandas as pd
from tqdm import tqdm
from xquant.factordata import FactorData
s = FactorData()
from xquant.marketdata import MarketData
mdp = MarketData()

start_date, end_date = 20201201, 20230531

index_list = ['000852.SH']
index_minute_data_path = '/data/group/800080/warehouseJG/prod/LOCAL_DATA/CSV/WIND/MINUTE/index_perdate/'

# 指数行情
index_md = IO.read_data([start_date, end_date], universe=index_list, columns=['S_DQ_OPEN', 'S_DQ_CLOSE'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5')
index_md = index_md.rename(columns={'S_DQ_OPEN': 'open', 'S_DQ_CLOSE': 'close'})

for index in tqdm(index_md.index):
    dt, code = index
    date = dt.strftime('%Y%m%d')
    tick_df = mdp.get_data_by_date('Index', code, date)
    index_md.loc[index, 'close_check'] = tick_df['LastPx'].iloc[-1]

    tick_df['MDTime'] = tick_df['MDTime'].astype(int)
    tick_df = tick_df[(tick_df['MDTime'] > 93000000) & (tick_df['MDTime'] < 145700000)]
    tick_df = tick_df[~((tick_df['MDTime'] > 113000000) & (tick_df['MDTime'] < 130000000))]
    index_md.loc[index, 'twap'] = tick_df['LastPx'].mean()
    index_md.loc[index, 'price_0940'] = tick_df[tick_df['MDTime'] >= 94000000]['LastPx'].iloc[0]
    index_md.loc[index, 'price_1000'] = tick_df[tick_df['MDTime'] >= 100000000]['LastPx'].iloc[0]

index_md = index_md.sort_values(['Ticker', 'dt'])
index_md['next_open'] = index_md.groupby('Ticker')['open'].shift(-1)
index_md['next_0940'] = index_md.groupby('Ticker')['price_0940'].shift(-1)
index_md['next_twap'] = index_md.groupby('Ticker')['twap'].shift(-1)

minute_df_close_all = []
for index in tqdm(index_md.index):
    dt, code = index
    date = pd.to_datetime(dt).strftime('%Y%m%d')
    minute_df = pd.read_pickle(index_minute_data_path + date + '.pkl', compression='gzip')
    minute_df = minute_df.reset_index()
    minute_df['dt'] = pd.to_datetime(minute_df['dt'].astype(str))
    minute_df['Ticker'] = minute_df['Ticker'].apply(lambda x: str(int(x)).zfill(6) + '.SH')
    minute_df = minute_df[minute_df['Ticker'].isin(index_md.loc[dt].index.get_level_values('Ticker'))]
    minute_df = minute_df[(minute_df['minute'] < 1457)]
    minute_df_close = minute_df.set_index(['dt', 'Ticker', 'minute'])['close'].unstack(level=-1)
    minute_df_close_all.append(minute_df_close)

minute_df_close_all = pd.concat(minute_df_close_all)
col_list = [col for col in minute_df_close_all.columns]
index_md[col_list] = minute_df_close_all
index_md['label_close_next_open'] = index_md['next_open'] / index_md['close'] - 1
index_md['label_next_open_next_0940'] = index_md['next_0940'] / index_md['next_open'] - 1
index_md['label_next_0940_next_twap'] = index_md['next_twap'] / index_md['next_0940'] - 1

index_md.to_pickle('/data/user/023859/Hedging/index_price_%s_%s.pkl'%(start_date,end_date))