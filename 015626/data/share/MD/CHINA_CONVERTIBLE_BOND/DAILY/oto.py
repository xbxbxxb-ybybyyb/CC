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
    am_930 = csvdf.loc[(idx.hour == 9) & (idx.minute == 30)].mean().to_frame().T.add_suffix('_mean_930')
    am_930_934 = csvdf.loc[(idx.hour == 9) & (idx.minute >= 30) & (idx.minute <= 34)].mean().to_frame().T.add_suffix('_mean_930_934')
    am_930_939 = csvdf.loc[(idx.hour == 9) & (idx.minute >= 30) & (idx.minute <= 39)].mean().to_frame().T.add_suffix('_mean_930_939')
    am_930_944 = csvdf.loc[(idx.hour == 9) & (idx.minute >= 30) & (idx.minute <= 44)].mean().to_frame().T.add_suffix('_mean_930_944')
    am_930_949 = csvdf.loc[(idx.hour == 9) & (idx.minute >= 30) & (idx.minute <= 49)].mean().to_frame().T.add_suffix('_mean_930_949')
    am_930_959 = csvdf.loc[(idx.hour == 9) & (idx.minute >= 30) & (idx.minute <= 59)].mean().to_frame().T.add_suffix('_mean_930_959')
    result = pd.concat([am_930, am_930_934, am_930_939, am_930_944, am_930_949, am_930_959], axis = 1)
    
    date = path.split('/')[-1][:8]
    result['Ticker'] = path.split('/')[-2]
    result['dt'] = date
    return result

pathlist = glob.glob('/arch1/group/800466/warehouse/prod/MD/CHINA_CONVERTIBLE_BOND/Tick/*/*.csv')

dflist = []
with Pool(processes = 24) as pool:
    dflist = pool.map(get_10mins_bidask_multitime, pathlist)
    
df = pd.concat(dflist, axis = 0)
df['dt'] = pd.to_datetime(df['dt'])
df = df.set_index(['dt','Ticker'])
df = df.sort_index()
df = df[~df.index.duplicated()].sort_index()
df = df.replace(0, np.nan)

label_dict = {'1':'930','5':'930_934','10':'930_939','15':'930_944','20':'930_949','30':'930_959'}
for k,v in label_dict.items():
    df['label_oto%s' % k] = (df['Buy1Price_mean_%s' % v].unstack().shift(-1) / df['Sell1Price_mean_%s' % v].unstack() - 1).stack()