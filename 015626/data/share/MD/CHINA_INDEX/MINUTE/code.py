from xquant.marketdata import MarketData
mdp = MarketData()
df = mdp.get_data_by_time_frame("Kline1M4ZT", "399006.SZ", "20170101 092500000", "20231107 150000250")
df

df['dt'] =df['MDDate'] + ' ' + df['MDTime']
df['dt'] = df['dt'].apply(lambda x:pd.to_datetime(x[:-3])) 

df['Ticker'] = '399006.SZ'

df.columns

df = df[['dt','Ticker','OpenPx', 'HighPx','LowPx','ClosePx', 'TotalVolumeTrade','TotalValueTrade']].set_index(['dt','Ticker'])


df.columns =  ['open', 'high', 'low', 'close', 'volume', 'amount']

df = df.reset_index(level = 1, drop = True).between_time('930','1456')

df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].fillna(method = 'ffill')
df[['volume', 'amount']] = df[['volume', 'amount']].fillna(0)

df.groupby(df.index.date)['open'].count().shape

df.to_pickle('/data/user/015626/data/share/MD/CHINA_INDEX/MINUTE/indexMinute_399006.pkl', compression='gzip')