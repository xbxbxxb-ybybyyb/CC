from xquant.marketdata import MarketData

import pandas as pd
pd.set_option('max_columns', 150)
import datetime 
from multifactor.IO import IO
import numpy as np
import os
from multiprocessing import Pool
import glob

def getdt(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')
    
def get_target_list(ticker, startdate, enddate):
    tickerdict = {'IC.CFE':'index_weight_zz500','IF.CFE':'index_weight_hs300','IH.CFE':'index_weight_sh50'}
    tickercolumn = tickerdict[ticker]
    indexweight = IO.read_data([startdate, enddate],columns = [tickercolumn], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
    indexweight = indexweight.unstack().shift(1).stack()
    universe = indexweight[indexweight[tickercolumn]>0]
    universe = universe.reset_index()
    universe['dt'] = universe.dt.apply(lambda x:int(str(x)[:10].replace('-','')))
    return np.array(universe).tolist()

def get_dt(a, b):
    year = a//10000
    month = a%10000//100
    day = a%100
    
    hour = b//100
    minute = b%100
    return datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),0)
    
def get_index_fromdate(date):
    t_mins_list = pd.date_range('09:30:00', '11:29:00', freq='min').to_list() + pd.date_range('13:00:00',
                                                                                              '14:57:00',
                                                                                              freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for m in t_mins_list:
        index_list.append(str(date) + ' ' + m)
    index_min = pd.DataFrame({'dt': index_list})
    index_min['dt'] = pd.to_datetime(index_min['dt'])
    return index_min.set_index('dt').sort_index()

def get_csvdf(para):
    print(para)
    csvpath = os.path.join(rootpath, str(para[0]), para[1] + '.csv')
    if not os.path.exists(csvpath):
        return
    try:
        csvdf = pd.read_csv(csvpath, index_col=0)
    except:
        return
    if 'close' in csvdf.columns.tolist():
        if csvdf['close'].sum() == 0:
            csvdf = csvdf.drop(['open','high','low','close'], axis = 1)
        if csvdf['volume'].sum() == 0:
            csvdf = csvdf.drop(['volume', 'amount'], axis = 1)

    csvdf.index = pd.DatetimeIndex(csvdf.index)
    if 'close' not in csvdf.columns.tolist():
        pickle_path = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock/'
        pdf = pd.read_pickle(os.path.join(pickle_path, 'UnAdjstedStockMinute_%s.pkl' % (para[1][:-3])), compression='gzip').reset_index(level = 1, drop = True).loc[para[0]].reset_index()
        pdf['dt'] = pdf.apply(lambda x:get_dt(x['dt'], x.minute), axis = 1)
        pdf = pdf.drop(['minute'], axis = 1).rename(columns = {'amt':'amount'}).set_index('dt')
        csvdf = csvdf.join(pdf, how = 'outer')

    csvdf = get_index_fromdate(para[0]).join(csvdf, how = 'left') 
    
    csv_columns = csvdf.columns.tolist()

    for k in ['open','high','low','close']:
        if k in csv_columns:
            csvdf[k] = csvdf[k].fillna(method = 'pad')
    res_columns = list(set(csv_columns) - set(['open','high','low','close']))
    for k in res_columns:
        if k in csv_columns:
            csvdf[k] = csvdf[k].fillna(0)

    csvdf['Ticker'] = para[1]

    return csvdf
      
import pickle
def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 
        
rootpath = '/data/user/015626/data/share/LOCAL_DATA/CSV/MINUTE/CHINA_STOCK/tick_transaction_tominute_v2/'
pickle_path = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock/'
paralist = get_target_list('IC.CFE',20150301,20200401)

dflist = []
with Pool(24) as pool:
    dflist = pool.map(get_csvdf, paralist)
    
df = pd.concat(dflist, axis = 0)
del(dflist)
df = df.dropna(subset = ['Ticker'])
df = df.reset_index().set_index(['dt','Ticker']).sort_index()

df = df.unstack(level = 1)
data_dict = {}
ticker = 'IC.CFE'
suffix_dict = {'IC.CFE':'_500','IF.CFE':'_300'}
for col in df.columns.get_level_values(0).unique():
    data_dict[col + suffix_dict[ticker]] = df[col]
    
save_pickle(data_dict, '/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/IC_cfg_hf_new_150301_200401.pkl')    
