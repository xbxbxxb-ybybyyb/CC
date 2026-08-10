# 制作隔夜收益数据，
import pandas as pd
import os
import numpy as np
from multifactor.IO import IO
import glob
from multiprocessing import Pool
from multifactor.data.utils import *
import multifactor.utility.dt as udt

def get_10mins_bidask_multitime(path):
    csvdf = pd.read_csv(path)[['dt','Buy1Price','Sell1Price', 'LastPx']]
    csvdf['dt'] = pd.to_datetime(csvdf['dt'])
    csvdf = csvdf.set_index('dt')
    csvdf = csvdf.replace(0, np.nan)
    csvdf = csvdf.fillna(method = 'ffill').fillna(method = 'bfill')
    
    idx = csvdf.index
    am_930_939 = csvdf.loc[(idx.hour == 9) & (idx.minute >= 30) & (idx.minute <= 39)].mean().to_frame().T.add_suffix('_mean_930_939')
    am_940_949 = csvdf.loc[(idx.hour == 9) & (idx.minute >= 40) & (idx.minute <= 49)].mean().to_frame().T.add_suffix('_mean_940_949')
    am_950_959 = csvdf.loc[(idx.hour == 9) & (idx.minute >= 50) & (idx.minute <= 59)].mean().to_frame().T.add_suffix('_mean_950_959')
    pm_1430_1439 = csvdf.loc[(idx.hour == 14) & (idx.minute >= 30) & (idx.minute <= 39)].mean().to_frame().T.add_suffix('_mean_1430_1439')
    pm_1440_1449 = csvdf.loc[(idx.hour == 14) & (idx.minute >= 40) & (idx.minute <= 49)].mean().to_frame().T.add_suffix('_mean_1440_1449')
    pm_1450_1459 = csvdf.loc[(idx.hour == 14) & (idx.minute >= 50) & (idx.minute <= 59)].mean().to_frame().T.add_suffix('_mean_1450_1459')
    
    pm_1400_1409 = csvdf.loc[(idx.hour == 14) & (idx.minute >= 0) & (idx.minute <= 9)].mean().to_frame().T.add_suffix('_mean_1400_1409')
    pm_1410_1419 = csvdf.loc[(idx.hour == 14) & (idx.minute >= 10) & (idx.minute <= 19)].mean().to_frame().T.add_suffix('_mean_1410_1419')
    pm_1420_1429 = csvdf.loc[(idx.hour == 14) & (idx.minute >= 20) & (idx.minute <= 29)].mean().to_frame().T.add_suffix('_mean_1420_1429')
    
    result = pd.concat([am_930_939, am_940_949, am_950_959, pm_1400_1409, pm_1410_1419, pm_1420_1429, pm_1430_1439, pm_1440_1449, pm_1450_1459], axis = 1)
    
    date = path.split('/')[-1][:8]
    contract = path.split('/')[-2]
    result['contract'] = contract + '.CFE'
    result['Ticker'] = contract[:2] + '.CFE'
    result['dt'] = date
    
    return result
    
def minute_flag_check(date):
    path1 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_stock_index_future_tick.success'
    return os.path.exists(path1) 
_, flag_date, _ = check_update_date()


flag_root = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(flag_date) + '/'
if not os.path.exists(flag_root):
    os.makedirs(flag_root)
flag_path_start = flag_root + str(flag_date) + '_' + 'future_overnight_return_multitime.start'
with open(flag_path_start,'w') as file:
    pass 


print('------wait tick flag')
while True:
    if minute_flag_check(flag_date):
        break
    time.sleep(60)
print('check flag finished!')


pathlist = glob.glob('/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/STOCK_INDEX_FUTURE/*/*.csv')

dflist = []
with Pool(processes = 4) as pool:
    dflist = pool.map(get_10mins_bidask_multitime, pathlist)
    
df = pd.concat(dflist, axis = 0)
df = df.set_index(['dt','contract'])
df = df.sort_index()
df = df.replace(0, np.nan)

dfunstack = df.unstack()
clist = dfunstack.columns.get_level_values(0).unique().tolist()
for am in ['Buy1Price_mean_930_939', 'Buy1Price_mean_940_949', 'Buy1Price_mean_950_959']:
    for pm in ['Sell1Price_mean_1400_1409', 'Sell1Price_mean_1410_1419', 'Sell1Price_mean_1420_1429', 'Sell1Price_mean_1430_1439', 'Sell1Price_mean_1440_1449', 'Sell1Price_mean_1450_1459']:
        df['long_ret_'+am.split('_')[-2]+'_'+pm.split('_')[-2]] = (dfunstack[am].shift(-1) / dfunstack[pm] - 1).stack()
        
for am in ['Sell1Price_mean_930_939', 'Sell1Price_mean_940_949', 'Sell1Price_mean_950_959']:
    for pm in ['Buy1Price_mean_1400_1409', 'Buy1Price_mean_1410_1419', 'Buy1Price_mean_1420_1429', 'Buy1Price_mean_1430_1439', 'Buy1Price_mean_1440_1449', 'Buy1Price_mean_1450_1459']:
        df['short_ret_'+am.split('_')[-2]+'_'+pm.split('_')[-2]] = (dfunstack[am].shift(-1) / dfunstack[pm] - 1).stack()

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

IO.pd_hdf5_writer(r, '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight_ret_multitime.h5', dataset='overnight_ret_multitime', override = True)

flag_path_success = flag_root + str(flag_date) + '_' + 'future_overnight_return_multitime.success'
with open(flag_path_success,'w') as file:
    pass 