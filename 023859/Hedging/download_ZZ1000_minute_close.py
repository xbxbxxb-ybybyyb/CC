import pandas as pd
from tqdm import tqdm
from xquant.factordata import FactorData
s = FactorData()

start_date, end_date = 20210701, 20220630

stock_minute_data_path = '/data/group/800080/warehouseJG/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock_perdate/'
ZZ1000_sw_weight = pd.read_pickle('/data/user/023859/Hedging/ZZ1000_sw_weight_%s_%s.pkl' % (start_date, end_date))

minute_close_df_all = []
for date in tqdm(ZZ1000_sw_weight.reset_index()['dt'].unique()):
    minute_df = pd.read_pickle(stock_minute_data_path + date + '.pkl', compression='gzip')
    minute_df = minute_df.reset_index()
    minute_df['dt'] = minute_df['dt'].astype(str)
    minute_df['Ticker'] = minute_df['Ticker'].apply(lambda x: str(int(x)).zfill(6))
    minute_df['Ticker'] = minute_df['Ticker'].apply(lambda x: x + '.SH' if x.startswith('6') else x + '.SZ')
    minute_df = minute_df[minute_df['Ticker'].isin(ZZ1000_sw_weight.loc[date].index.get_level_values('Ticker'))]
    minute_df = minute_df[(minute_df['minute'] < 1457)]

    minute_close_df = minute_df.set_index(['dt', 'Ticker', 'minute'])['close'].unstack(level=-1)
    minute_close_df_all.append(minute_close_df)

minute_close_df_all = pd.concat(minute_close_df_all)
minute_close_df_all.to_pickle('/data/user/023859/Hedging/ZZ1000_minute_close_%s_%s.pkl'%(start_date,end_date))