from multifactor.IO import IO
import pandas as pd
import os
import datetime
from multifactor.data.utils import *
from multiprocessing.pool import Pool
    
csvpath = '/data/user/015626/data/share/LOCAL_DATA/CSV/MINUTE/cfg_juhe/'

def minute_flag_check(date):
    path = '/data/group/800080/warehouse/prod/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_' + 'MINUTE.success'
    return os.path.exists(path)

def ticker_match(ticker_num): # jit slow
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num>=600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num)))*'0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker
    
def create_df(h):
    h1 = h.unstack()
    hc = h1 - h1.shift(1)
    tempdf = pd.DataFrame()
    # Counts
    upclose = (hc['close']>0).sum(axis = 1)
    downclose = (hc['close']<0).sum(axis = 1)
    upvolume = (hc['volume'] > 0).sum(axis = 1)
    downvolume = (hc['volume'] < 0).sum(axis = 1)
    uphigh = (hc['high'] > 0).astype(int).sum(axis = 1)
    downhigh = (hc['high'] < 0).astype(int).sum(axis = 1)
    uplow = (hc['low'] > 0).astype(int).sum(axis = 1)
    downlow = (hc['low'] < 0).astype(int).sum(axis = 1)

    upco = ((h1['close']-h1['open']).fillna(0) > 0).sum(axis = 1)
    downco = ((h1['close']-h1['open']).fillna(0) < 0).sum(axis = 1)
    opentohighmean = (h1['open']-h1['high'].shift(1)>0).sum(axis = 1)
    opentolowmean = (h1['open']-h1['low'].shift(1)<0).sum(axis = 1)
    upopentoclose = (h1['open']-h1['close'].shift(1)>0).sum(axis = 1)
    downopentoclose = (h1['open']-h1['close'].shift(1)<0).sum(axis = 1)
    # Means
    retmean = hc['close'].mean(axis = 1)
    volumemean = h1['volume'].mean(axis = 1)
    rettovolume = (hc['close']/h1['volume']).mean(axis = 1)
    vwaptovolume = (h1['amt']/h1['volume']/h1['volume']).mean(axis = 1)
    closetoopenmean = ((h1['close']-h1['open'])).mean(axis = 1)
    highlowmean = ((h1['high']-h1['low'])).mean(axis = 1)
    # Note: all of below are in terms of 1 minute
    # Number of stocks with positive returns in closing prices
    tempdf['upclose'] = upclose
    # Number of stocks with negative returns in closing prices
    tempdf['downclose'] = downclose
    # Number of stocks with rising volume
    tempdf['upvolume'] = upvolume
    # Number of stocks with falling volume
    tempdf['downvolume'] = downvolume
    # Number of stocks with rising highs
    tempdf['uphigh'] = uphigh
    # Number of stocks with falling highs
    tempdf['downhigh'] = downhigh
    # Number of stocks with rising lows
    tempdf['uplow'] = uplow
    # Number of stocks with falling lows
    tempdf['downlow'] = downlow
    # Number of stocks whose closing prices are higher than their opening prices
    tempdf['upco'] = upco
    # Number of stocks whose closing prices are lower than their opening prices
    tempdf['downco'] = downco
    # mean(open - previous high)
    tempdf['upopentohigh'] = opentohighmean
    # mean(open - previous low)
    tempdf['downopentolow'] = opentolowmean
    # Number of stocks whose (open > previous close)
    tempdf['upopentoclose'] = upopentoclose
    # Number of stocks whose (open < previous close)
    tempdf['downopentoclose'] = downopentoclose
    # Mean of returns in closing prices
    tempdf['retmean'] = retmean
    # Mean of volume for all
    tempdf['volumemean'] = volumemean
    # Mean of return to volume
    tempdf['rettovolume'] = rettovolume
    # Mean of vwap to volume
    tempdf['vwaptovolume'] = vwaptovolume
    # Mean of close - open
    tempdf['closetoopenmean'] = closetoopenmean
    # Mean of high - low
    tempdf['highlowmean'] = highlowmean
    return tempdf
    
namedict = {'IC.CFE':'index_weight_zz500','IF.CFE':'index_weight_hs300','IH.CFE':'index_weight_sh50'}

def get_cfg_bydate(date):
    print(date)
    spot_data = pd.read_pickle('/data/group//800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock_perdate/%s.pkl' % date, compression='gzip')
    spot_data = spot_data.reset_index()
    spot_data['dt'] = spot_data['dt'] * 1E6 + spot_data['minute'] * 100
    spot_data['dt'] = pd.to_datetime(spot_data['dt'].astype('int'), format='%Y%m%d%H%M%S')
    spot_data['Ticker'] = spot_data.Ticker.apply(lambda x:ticker_match(x))
    spot_data = spot_data.drop(['minute'], axis = 1)

    indexweight = IO.read_data([date], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
    resultdf = pd.DataFrame()
    for indexname in ['IC.CFE','IF.CFE','IH.CFE']:
        weightcol = namedict[indexname]
        cfgweightdf = indexweight[indexweight[weightcol] > 0].reset_index()
        cfgweightdf['dt'] = cfgweightdf['dt'].apply(lambda x:int(datetime.datetime.strftime(x,'%Y%m%d')))

        tickerlist = cfgweightdf[cfgweightdf.dt == date].Ticker.tolist()
        cfgdf = spot_data[spot_data.Ticker.isin(tickerlist)]

        cfgdf = cfgdf.set_index(['dt','Ticker']).sort_index()

        c = create_df(cfgdf)
        c['Ticker'] = indexname
        resultdf = resultdf.append(c)
    resultdf = resultdf.reset_index().set_index(['dt','Ticker']).sort_index()
    resultdf.to_csv(csvpath + str(date) + '.csv')
    
sdate,_,cdate_list = check_update_date()

print('------wait minute flag')
while True:
    if minute_flag_check(sdate):
        break
print('start generate data')

# with Pool(processes = 24) as pool:
    # pool.map(get_cfg_bydate, cdate_list)

for date in cdate_list:
    get_cfg_bydate(date)
    
totaldf = pd.DataFrame()
for date in cdate_list:
    print('csv to h5: ', date)
    df = pd.read_csv(csvpath + str(date) + '.csv')
    df['dt'] = pd.to_datetime(df['dt'])
    totaldf = totaldf.append(df)

totaldf = totaldf.sort_values(['dt','Ticker'])
totaldf = totaldf.set_index(['dt','Ticker'])

idx = totaldf.index.get_level_values(0)
t1 = totaldf.loc[(idx.hour == 9) & (idx.minute >= 30)]
t2 = totaldf.loc[(idx.hour == 10) | (idx.hour == 13)]
t3 = totaldf.loc[(idx.hour == 11) & (idx.minute < 30)]
t4 = totaldf.loc[(idx.hour == 14) & (idx.minute <= 57)]
t = t1.append(t2).append(t3).append(t4)
t = t.sort_index()

h5path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/MD_STOCK_INDEX_CFG_MINUTE.h5'
IO.pd_hdf5_writer(t, h5path, dataset='cfg', append=True)