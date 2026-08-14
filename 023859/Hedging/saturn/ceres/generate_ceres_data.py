import pandas as pd
from tqdm import tqdm

start_date, end_date = 20201201, 20230531

stock_minute_data_path = '/data/group/800080/warehouseJG/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock_perdate/'
df_ceres = pd.read_csv('/dfs/user/023859/Hedging/ceres/集成信号_20201201_20230531.csv',index_col=0)
df_ceres['dt'] = pd.to_datetime(df_ceres['dt'])
df_ceres = df_ceres.set_index(['dt','Ticker'])

minute_df_hl_amt_all = []
minute_df_ft_amt_all = []
minute_df_close_all = []

for dt in tqdm(df_ceres.reset_index()['dt'].unique()):
    date = pd.to_datetime(dt).strftime('%Y%m%d')
    minute_df = pd.read_pickle(stock_minute_data_path + date + '.pkl', compression='gzip')
    minute_df = minute_df.reset_index()
    minute_df['dt'] = pd.to_datetime(minute_df['dt'].astype(str))
    minute_df['Ticker'] = minute_df['Ticker'].apply(lambda x: str(int(x)).zfill(6))
    minute_df['Ticker'] = minute_df['Ticker'].apply(lambda x: x + '.SH' if x.startswith('6') else x + '.SZ')
    minute_df = minute_df[minute_df['Ticker'].isin(df_ceres.loc[dt].index.get_level_values('Ticker'))]
    minute_df = minute_df[(minute_df['minute'] < 1457)]
    minute_df['cum_high'] = minute_df.groupby(['dt', 'Ticker'])['high'].cummax()  # 最高价从开盘开始计算
    minute_df['cum_low'] = minute_df.groupby(['dt', 'Ticker'])['low'].cummin()  # 最高价从开盘开始计算
    minute_df['hl_amt'] = minute_df['cum_high'] - minute_df['close']
    minute_df['ft_amt'] = minute_df['close'] - minute_df['cum_low']
    minute_df_hl_amt = minute_df.set_index(['dt', 'Ticker', 'minute'])['hl_amt'].unstack(level=-1)
    minute_df_ft_amt = minute_df.set_index(['dt', 'Ticker', 'minute'])['ft_amt'].unstack(level=-1)
    minute_df_close = minute_df.set_index(['dt', 'Ticker', 'minute'])['close'].unstack(level=-1) # 分钟收盘价序列

    minute_df_hl_amt_all.append(minute_df_hl_amt)
    minute_df_ft_amt_all.append(minute_df_ft_amt)
    minute_df_close_all.append(minute_df_close)

minute_df_hl_amt_all = pd.concat(minute_df_hl_amt_all)
minute_df_ft_amt_all = pd.concat(minute_df_ft_amt_all)
minute_df_close_all = pd.concat(minute_df_close_all)

minute_df_hl_amt_all.to_pickle('/data/user/023859/Hedging/ceres/ceres_minute_high_to_close_amt_%s_%s.pkl'%(start_date,end_date))
minute_df_ft_amt_all.to_pickle('/data/user/023859/Hedging/ceres/ceres_minute_close_to_low_amt_%s_%s.pkl'%(start_date,end_date))
minute_df_close_all.to_pickle('/data/user/023859/Hedging/ceres/ceres_minute_close_%s_%s.pkl'%(start_date,end_date))