import pandas as pd
from multifactor.IO import IO
from multiprocessing import Pool
import multifactor.utility.dt as udt
import os
import numpy as np
import glob
from tqdm import tqdm

def juhe_csv(path):
    fudf = pd.read_csv(path,index_col=0,parse_dates=True)[['open','high','low','close','volume','value','vwap','position']]
    fudf = fudf.rename(columns={'value':'amount'})
    fudf['Ticker'] = path.split('/')[-2] + '.CFE'
    fudf.index.names = ['dt']
    fudf = fudf.reset_index().set_index(['dt','Ticker'])
    return fudf

pathlistic = glob.glob('/data/user/015626/data/share/LOCAL_DATA/CSV/MINUTE/CHINA_FUTURES/tick_to_15s/ALL_CONTRACT/IC*/*')
pathlistif = glob.glob('/data/user/015626/data/share/LOCAL_DATA/CSV/MINUTE/CHINA_FUTURES/tick_to_15s/ALL_CONTRACT/IF*/*')
pathlist = pathlistic + pathlistif

print('juhe futures csv')
fulist = []
with Pool(24) as pool:
    fulist = pool.map(juhe_csv, pathlist)
    
fudf = pd.concat(fulist, axis = 0).sort_index()
print('write futures h5')
IO.pd_hdf5_writer(fudf,'/data/user/015626/data/share/MD/CHINA_FUTURES/15s/IC_IF_15s_data.h5', dataset = 'IC_IF_15s_data')

namedict = {'HS300':'000300.SH',
            'ZZ500':'000905.SH',
            'SH50':'000016.SH'}

def juhe_csv_index(path):
    indf = pd.read_csv(path,index_col=0,parse_dates=True)[['open','high','low','close','volume','value']]
    indf = indf.rename(columns={'value':'amount'})
    indf['Ticker'] = namedict[path.split('/')[-2]]
    indf.index.names = ['dt']
    indf = indf.reset_index().set_index(['dt','Ticker'])
    return indf

pathlist300 = glob.glob('/data/user/015626/data/share/LOCAL_DATA/CSV/tick_to_15s/CHINA_INDEX/HS300/*')
pathlist500 = glob.glob('/data/user/015626/data/share/LOCAL_DATA/CSV/tick_to_15s/CHINA_INDEX/ZZ500/*')
pathlist = pathlist300 + pathlist500
print('juhe index csv')
inlist = []
with Pool(24) as pool:
    inlist = pool.map(juhe_csv_index, pathlist)
    
indf = pd.concat(inlist, axis = 0).sort_index()
print('write index h5')
IO.pd_hdf5_writer(indf,'/data/user/015626/data/share/MD/CHINA_INDEX/15s/HS300_ZZ500_15s_data.h5', dataset = 'HS300_ZZ500_15s_data')