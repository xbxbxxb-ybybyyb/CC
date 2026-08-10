# 制作隔夜收益数据，包含10分钟与5分钟的，中间一根#分割线后为5分钟的
import pandas as pd
import os
import numpy as np
from multifactor.IO import IO
import glob
from multiprocessing import Pool
from multifactor.data.utils import *
import multifactor.utility.dt as udt

def get_10mins_bidask(path):
    csvdf = pd.read_csv(path)[['dt','Buy1Price','Sell1Price', 'LastPx']]
    csvdf['dt'] = pd.to_datetime(csvdf['dt'])
    csvdf = csvdf.set_index('dt')
    csvdf = csvdf.replace(0, np.nan)
    csvdf = csvdf.fillna(method = 'ffill').fillna(method = 'bfill')
    
    idx = csvdf.index
    morning = csvdf.loc[(idx.hour == 9) & (idx.minute >= 30) & (idx.minute <= 39)].mean().to_frame().T.add_suffix('_am')
    afternoon = csvdf.loc[(idx.hour == 14) & (idx.minute >= 40) & (idx.minute <= 49)].mean().to_frame().T.add_suffix('_pm')
    result = morning.join(afternoon)
    
    date = path.split('/')[-1][:8]
    contract = path.split('/')[-2]
    result['contract'] = contract + '.CFE'
    result['Ticker'] = contract[:2] + '.CFE'
    result['dt'] = date
    
    return result
print('start')
pathlist = glob.glob('/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/STOCK_INDEX_FUTURE/*/*.csv')

dflist = []
with Pool(processes = 24) as pool:
    dflist = pool.map(get_10mins_bidask, pathlist)
    
df = pd.concat(dflist, axis = 0)
df = df.set_index(['dt','contract'])
df = df.sort_index()


df = df.unstack(level = 1)
df['Buy1Price_am'] = df['Buy1Price_am'].shift(-1)
df['Sell1Price_am'] = df['Sell1Price_am'].shift(-1)

df = df.stack()
df = df.replace(0, np.nan)

df['long_ret'] = df.Buy1Price_am / df.Sell1Price_pm - 1
df['short_ret'] = df.Sell1Price_am / df.Buy1Price_pm - 1

df = df.reset_index()
df['dt'] = pd.to_datetime(df['dt'])
totaldf = df.set_index(['dt','Ticker','contract'])

# 以下是近月合约
univ = IO.read_data([20100101,21000101],columns = ['contract_00'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
univ = univ.reset_index().set_index(['dt','Ticker','contract_00'])
univ = univ.reset_index().rename(columns = {'contract_00':'contract'}).set_index(['dt','Ticker','contract'])

df = totaldf.join(univ, how = 'inner').sort_index()

#去除节假日
df = df.reset_index()
datelist = df.dt.tolist()
datedict = {}
for i in range(len(datelist) - 1):
    datedict[datelist[i]] = (datelist[i+1] - datelist[i]).days
daterange = pd.DataFrame(datedict, index = ['days']).T
deletelist = daterange[~daterange.days.isin([1,3])].index.tolist()
r = df[~df.dt.isin(deletelist)]
r = r.set_index(['dt','Ticker'])

IO.pd_hdf5_writer(r, '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight_ret_4049.h5', dataset='overnight_ret_4049')