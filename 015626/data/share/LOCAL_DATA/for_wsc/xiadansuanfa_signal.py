factor = pd.read_pickle('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/20221028_ic_ic_v7c/model_value/model_norm/20221104/pred_comb2.pkl')
factor = factor * 2 - 1

ticker = 'IC.CFE'
start_date = 20210101
end_date = 20221231
std_adjust = True
signal_name = 'v7c'

start_date_temp = int(udt.get_trading_day_offset(start_date, -2)[0].strftime('%Y%m%d'))
end_date_temp = int(udt.get_trading_day_offset(end_date, 2)[0].strftime('%Y%m%d'))
today = str(int(datetime.datetime.now().strftime('%Y%m%d')))


# 计算std
data = IO.read_data([start_date_temp,end_date_temp],columns = ['close'], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_FUTURES/MINUTE/%s_MINUTE.h5' % (ticker[:2]))
data = data.reset_index(level = 1).between_time('930', '1456').reset_index().set_index(['dt','Ticker'])
data = data.unstack()['close'].pct_change().rolling(30,min_periods=15).std().stack().reset_index(level = 1)
data.columns = ['Ticker', 'std30']
univ = IO.read_data([start_date_temp,end_date_temp], columns = ['contract_00'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
univ = univ.xs(ticker, level = 1)
data = univ.reindex(data.index.unique(), method = 'pad').join(data)
ret_std = data[data.Ticker == data.contract_00][['std30']].sort_index()

if isinstance(factor, pd.Series):
    factor = factor.to_frame()
factor = ret_std.join(factor, how = 'inner')
factor.columns = ['std','value']
signal1 = factor['value']
signal2 = factor['std'] * factor['value']

pos_divnum = 10
pos_dict1 = {(0,   0.3): (0,         0),
            (0.3, 0.4): (0,         0.5/10),
            (0.4, 0.8): (0,         1/10),
            (0.8, 0.9): (0.5/10,    1/10),
            (0.9, 100): (1/10,      1/10)}

pos_dict2 = {(0,     0.0002): (0,        0),
            (0.0002, 0.0003): (0,        0.333/pos_divnum),
            (0.0003, 0.0004): (0,        0.666/pos_divnum),
            (0.0004, 0.0005): (0,        1/pos_divnum),
            (0.0005, 0.0006): (0,        1/pos_divnum),
            (0.0006, 0.0007): (0.333/pos_divnum, 1/pos_divnum),
            (0.0007, 0.0008): (0.666/pos_divnum, 1/pos_divnum),
            (0.0008, 100):    (1/pos_divnum,     1/pos_divnum)}


signal_list1 = [{'signal':signal1,'pos_dict':pos_dict1,'cash':1e8}, {'signal':signal2,'pos_dict':pos_dict2,'cash':1e8}]

factor = pd.read_pickle('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/20221028_ic_ic_short_v3c/model_value/model_norm/20221104/pred_comb2.pkl')
factor = factor * 2 - 1

ticker = 'IC.CFE'
start_date = 20210101
end_date = 20221231
std_adjust = True
signal_name = 'v7c'

start_date_temp = int(udt.get_trading_day_offset(start_date, -2)[0].strftime('%Y%m%d'))
end_date_temp = int(udt.get_trading_day_offset(end_date, 2)[0].strftime('%Y%m%d'))
today = str(int(datetime.datetime.now().strftime('%Y%m%d')))


# 计算std
data = IO.read_data([start_date_temp,end_date_temp],columns = ['close'], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_FUTURES/MINUTE/%s_MINUTE.h5' % (ticker[:2]))
data = data.reset_index(level = 1).between_time('930', '1456').reset_index().set_index(['dt','Ticker'])
data = data.unstack()['close'].pct_change().rolling(30,min_periods=15).std().stack().reset_index(level = 1)
data.columns = ['Ticker', 'std30']
univ = IO.read_data([start_date_temp,end_date_temp], columns = ['contract_00'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
univ = univ.xs(ticker, level = 1)
data = univ.reindex(data.index.unique(), method = 'pad').join(data)
ret_std = data[data.Ticker == data.contract_00][['std30']].sort_index()

if isinstance(factor, pd.Series):
    factor = factor.to_frame()
factor = ret_std.join(factor, how = 'inner')
factor.columns = ['std','value']
signal1 = factor['value']
signal2 = factor['std'] * factor['value']

pos_divnum = 10
pos_dict1 = {(0,   0.3): (0,         0),
            (0.3, 0.4): (0,         0.5/10),
            (0.4, 0.8): (0,         1/10),
            (0.8, 0.9): (0.5/10,    1/10),
            (0.9, 100): (1/10,      1/10)}

pos_dict2 = {(0,     0.0002): (0,        0),
            (0.0002, 0.0003): (0,        0.333/pos_divnum),
            (0.0003, 0.0004): (0,        0.666/pos_divnum),
            (0.0004, 0.0005): (0,        1/pos_divnum),
            (0.0005, 0.0006): (0,        1/pos_divnum),
            (0.0006, 0.0007): (0.333/pos_divnum, 1/pos_divnum),
            (0.0007, 0.0008): (0.666/pos_divnum, 1/pos_divnum),
            (0.0008, 100):    (1/pos_divnum,     1/pos_divnum)}


signal_list2 = [{'signal':signal1,'pos_dict':pos_dict1,'cash':1e8}]

signal_list = signal_list1 + signal_list2