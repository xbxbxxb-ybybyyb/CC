# 制作隔夜收益数据，包含10分钟与5分钟的，中间一根#分割线后为5分钟的
import pandas as pd
import os
import numpy as np
from multifactor.IO import IO
import glob
from multiprocessing import Pool
from multifactor.data.utils import *
import multifactor.utility.dt as udt

def get_10mins_bidask_multitime(path):
    csvdf = pd.read_csv(path)[['dt','Buy1Price','Sell1Price']]
    csvdf['dt'] = pd.to_datetime(csvdf['dt'])
    csvdf = csvdf.set_index('dt')
    csvdf = csvdf.replace(0, np.nan)
#    csvdf = csvdf.fillna(method = 'ffill').fillna(method = 'bfill')
    
    idx = csvdf.index
    am_930_939 = csvdf.loc[(idx.hour == 9) & (idx.minute >= 30) & (idx.minute <= 39)].mean().to_frame().T.add_suffix('_mean_930_939')
    am_940_949 = csvdf.loc[(idx.hour == 9) & (idx.minute >= 40) & (idx.minute <= 49)].mean().to_frame().T.add_suffix('_mean_940_949')
    am_950_959 = csvdf.loc[(idx.hour == 9) & (idx.minute >= 50) & (idx.minute <= 59)].mean().to_frame().T.add_suffix('_mean_950_959')
    pm_1430_1439 = csvdf.loc[(idx.hour == 14) & (idx.minute >= 30) & (idx.minute <= 39)].mean().to_frame().T.add_suffix('_mean_1430_1439')
    pm_1440_1449 = csvdf.loc[(idx.hour == 14) & (idx.minute >= 40) & (idx.minute <= 49)].mean().to_frame().T.add_suffix('_mean_1440_1449')
    pm_1450_1459 = csvdf.loc[(idx.hour == 14) & (idx.minute >= 50) & (idx.minute <= 59)].mean().to_frame().T.add_suffix('_mean_1450_1459')
    result = pd.concat([am_930_939, am_940_949, am_950_959, pm_1430_1439, pm_1440_1449, pm_1450_1459], axis = 1)
    
    date = path.split('/')[-1][:8]
    result['Ticker'] = path.split('/')[-2]
    result['dt'] = date
    return result
print('start')
_,_,cdate_list = check_update_date(20210627,20210826)
pathlist = []
for cdate in cdate_list:
    pathlist = pathlist + glob.glob('/arch1/group/800466/warehouse/prod/MD/CHINA_CONVERTIBLE_BOND/Tick/*/%s.csv' % str(cdate))
#pathlist = glob.glob('/arch1/group/800466/warehouse/prod/MD/CHINA_CONVERTIBLE_BOND/Tick/*/*.csv')
#pathlist = glob.glob('/arch1/group/800466/warehouse/prod/MD/CHINA_FUND/ETF/Tick/*/*.csv')

dflist = []
with Pool(processes = 24) as pool:
    dflist = pool.map(get_10mins_bidask_multitime, pathlist)
    
df = pd.concat(dflist, axis = 0)
df['dt'] = pd.to_datetime(df['dt'])
df = df.set_index(['dt','Ticker'])
df = df.sort_index()
df = df[~df.index.duplicated()].sort_index()
df = df.replace(0, np.nan)

dfunstack = df.unstack()
clist = dfunstack.columns.get_level_values(0).unique().tolist()
for am in ['Buy1Price_mean_930_939', 'Buy1Price_mean_940_949', 'Buy1Price_mean_950_959']:
    for pm in ['Sell1Price_mean_1430_1439', 'Sell1Price_mean_1440_1449', 'Sell1Price_mean_1450_1459']:
        df['long_ret_'+am.split('_')[-2]+'_'+pm.split('_')[-2]] = (dfunstack[am].shift(-1) / dfunstack[pm] - 1).stack()
        
for am in ['Sell1Price_mean_930_939', 'Sell1Price_mean_940_949', 'Sell1Price_mean_950_959']:
    for pm in ['Buy1Price_mean_1430_1439', 'Buy1Price_mean_1440_1449', 'Buy1Price_mean_1450_1459']:
        df['short_ret_'+am.split('_')[-2]+'_'+pm.split('_')[-2]] = (dfunstack[am].shift(-1) / dfunstack[pm] - 1).stack()

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

IO.pd_hdf5_writer(r, '/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/DAILY/overnight_ret_kzz.h5', dataset='overnight_ret_kzz', append = True)
#IO.pd_hdf5_writer(r, '/data/user/015626/data/share/MD/CHINA_FUND/ETF/DAILY/overnight_ret_etf.h5', dataset='overnight_ret_etf')