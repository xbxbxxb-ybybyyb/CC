dfd = IO.read_data([20110101,20230909],columns = ['open'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_SIF_TICK_TO_DAILY_ALL_CONTRACT.h5')
dfm = IO.read_data(columns = ['close'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_ALL_CONTRACT.h5')

dfm930 = dfm.reset_index(level = 1).at_time(datetime.time(9,30))
dfm934 = dfm.reset_index(level = 1).at_time(datetime.time(9,34))

dfm930.index = [pd.to_datetime(x.date()) for x in dfm930.index]
dfm934.index = [pd.to_datetime(x.date()) for x in dfm934.index]

dfm930.index.name = 'dt'
dfm934.index.name = 'dt'

dfm930 = dfm930.set_index('Ticker', append = True)
dfm934 = dfm934.set_index('Ticker', append = True)

df = pd.concat([dfd, dfm930.add_suffix('_930'), dfm934.add_suffix('_934')], axis = 1)

os.makedirs('/data/user/015626/data/share/LOCAL_DATA/future_open')

df['ret_930'] = df['close_930'] / df['open'] - 1
df['ret_934'] = df['close_934'] / df['open'] - 1

df.to_pickle('/data/user/015626/data/share/LOCAL_DATA/future_open/all_futures.pkl')

univ = IO.read_data([20110101,20230909],columns=['contract_00'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')

univ = univ.reset_index(level = 1, drop = True).rename(columns = {'contract_00':'Ticker'}).set_index('Ticker', append = True)

df.reindex(univ.index).to_pickle('/data/user/015626/data/share/LOCAL_DATA/future_open/futures_recent_month_open.pkl')