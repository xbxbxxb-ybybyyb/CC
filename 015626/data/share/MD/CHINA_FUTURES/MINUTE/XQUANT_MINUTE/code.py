df = IO.read_data([20200706, 20200707], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_ALL_CONTRACT.h5')
# df = IO.read_data([20200706, 20200707], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5')


rlist = []
for ticker in ['IH2007', 'IH2008', 'IH2009', 'IH2012']:
    tick = pd.read_csv(f'/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/STOCK_INDEX_FUTURE/{ticker}/20200706.csv', index_col=0, parse_dates=True)
    tick['amount'] = tick['TotalValueTrade'].diff()
    tick['volume'] = tick['TotalVolumeTrade'].diff()

    tick['open'] = tick['LastPx']
    tick['high'] = tick['LastPx']
    tick['low'] = tick['LastPx']
    tick['close'] = tick['LastPx']
    tick['twap'] = tick['LastPx']
    tick['position'] = tick['OpenInterest']
    tick = tick.resample('1min').agg({'open':'first','high':'max','low':'min','close':'last','twap':'mean','amount':'sum','volume':'sum','position':'last'})
    tick = tick.between_time('1440','1457')
    tick['vwap']  = tick['amount'] / tick['volume'] / 300
    tick['Ticker'] = ticker + '.CFE'
    tick = tick.set_index('Ticker', append = True)
    rlist.append(tick)
rr = pd.concat(rlist).sort_index()

df.update(rr)

rootpath = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/'
allcontract_path = os.path.join(rootpath, 'MD_SIF_TICK_TO_MINUTE_ALL_CONTRACT.h5')
recentmonth_path = os.path.join(rootpath, 'MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5')
main_path = os.path.join(rootpath, 'MD_SIF_TICK_TO_MINUTE_MAIN.h5')

IO.pd_hdf5_writer(df, allcontract_path, dataset = 'contract', append = True)

def date_to_min_index(df, ticker, future_kind):
    indexdf = df.xs(ticker, level=1)[[future_kind]]
    t_days_list = udt.get_trading_date_range(str(indexdf.index[0].date()).replace('-', ''),
                                             str(indexdf.index[-1].date()).replace('-', ''))
    t_days_list = [str(i)[:10] for i in t_days_list]
    t_mins_list = pd.date_range('09:30:00', '11:29:00', freq='min').to_list() + pd.date_range('13:00:00',
                                                                                              '14:57:00',
                                                                                              freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for d in t_days_list:
        for m in t_mins_list:
            index_list.append(d + ' ' + m)
    index_min = pd.DataFrame({'dt': index_list})
    index_min['dt'] = pd.to_datetime(index_min['dt'])
    index_min['date'] = index_min['dt'].apply(lambda x: x.date())
    index_min['date'] = pd.to_datetime(index_min['date'])

    indexdf = indexdf.reset_index().rename(columns={'dt': 'date', future_kind: 'Ticker'})
    indexdf = pd.merge(indexdf, index_min, on='date')
    indexdf = indexdf[['dt', 'Ticker']].set_index(['dt', 'Ticker'])
    return indexdf

alldf_origin = df.copy()
idf_origin = IO.read_data([20200706, 20200706], alt='/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')

print('update recent month')
# 更新近月合约数据
rdf = pd.DataFrame()
for ticker in ['IC.CFE','IF.CFE','IH.CFE']:
    alldf = alldf_origin.copy()

    idf = idf_origin.copy()
    idf = date_to_min_index(idf, ticker, future_kind='contract_00')

    alldf = alldf.join(idf, how='inner')
    origindata = alldf.reset_index().drop('PROD_ID', axis = 1).rename(columns = {'Ticker':'contract_00'})
    origindata['Ticker'] = ticker
    origindata = origindata.set_index(['dt','Ticker']).sort_index()
    
    rdf = rdf.append(origindata)
    
rdf = rdf.sort_index()


rdf

IO.pd_hdf5_writer(rdf, recentmonth_path, dataset='recent_month', append = True)


print('update mask')
pv = ['open', 'close', 'high', 'low', 'amount', 'volume', 'vwap', 'twap','position','share']
c = ['AbsDistance', 'BASCorrV', 'BASSign', 'BASWeighted', 'BidAskMean', 'BidAskVol', 'HighVolumeCount', 'OrderFlowImbalanceLv1', 'OrderFlowImbalanceRatioLv1', 'PriceKurt', 'PriceMean', 'PriceSkew', 'PriceVol', 'RetKurt', 'RetMean', 'RetSkew', 'RetVol', 'VolumeMean', 'VolumeStd']
c = c + pv
futures_data = IO.read_data([20200101, 21000101],columns = c, alt=os.path.join('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_ALL_CONTRACT.h5'))
futures_data = futures_data.reset_index()
futures_data['contract'] = futures_data.Ticker.apply(lambda x: x[2:])
futures_data['Ticker'] = futures_data.Ticker.apply(lambda x: x[:2] + x[-4:])
futures_data = futures_data.set_index(['dt', 'contract', 'Ticker'])

df = futures_data.unstack(level = 1)

u = IO.read_data([20200101, 21000101], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
u = u.xs('IF.CFE', level = 1)[['contract_00']]
u['contract'] = u.contract_00.apply(lambda x:x[2:])
u = u.reset_index().rename(columns = {'dt':'date'})[['date','contract']].set_index('date')

t_days_list = udt.get_trading_date_range(str(u.index[0].date()).replace('-',''),str(u.index[-1].date()).replace('-',''))
t_days_list = [str(i)[:10] for i in t_days_list]
t_mins_list = pd.date_range('09:30:00','11:29:00', freq='min').to_list() + pd.date_range('13:00:00','14:57:00', freq='min').to_list()
t_mins_list = [str(i)[-8:] for i in t_mins_list]
index_list = []
for d in t_days_list:
    for m in t_mins_list:
        index_list.append(d + ' ' + m)
index_df = pd.DataFrame({'dt':index_list})
index_df['dt'] = pd.to_datetime(index_df['dt'])
index_df['date'] = index_df.dt.apply(lambda x:x.date())
index_df = index_df.set_index('date')

udf = index_df.join(u).reset_index().set_index(['dt','contract']).sort_index()
udf['date'] = 100
udf = udf.unstack().droplevel(0, axis = 1)

mask = udf > 0

maskcolumns = mask.columns.tolist()

future_dict = {}
for x in ['IC.CFE','IF.CFE','IH.CFE','IM.CFE']:
    try:
        d = df.xs(x, level = 1)
    except:
        continue
    if x == 'IC.CFE':
        su = ''
    if x == 'IF.CFE':
        su = '_if'
    if x == 'IH.CFE':
        su = '_ih'
    if x == 'IM.CFE':
        su = '_im'
    for c in d.columns.get_level_values(0).unique():
        future_dict[c + su] = d[c].sort_index()
        
maskclist = mask.columns.tolist()
allclist = future_dict['open_if'].columns.tolist()
reslist = list(set(allclist) - set(maskclist))
for c in reslist:
    mask[c] = False
mask = mask.sort_index(axis = 1)

future_dict['recent_month_mask'] = mask

import pickle
def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 

#future_dict.update(main_mask_dict)
save_pickle(future_dict, '/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/FUTURE_DATA_2020.pkl')
