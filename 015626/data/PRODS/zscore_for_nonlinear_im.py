import pandas as pd
import numpy as np
from shutil import copyfile
import os
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import pickle
from functools import partial
from joblib import Parallel, delayed
import datetime
import warnings
warnings.filterwarnings('ignore')
import bottleneck as bk
import datetime
from multifactor.data.utils import *
from datetime import timedelta
from multiprocessing.pool import Pool
import matplotlib.pyplot as plt

kind = 'im'

flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'

_,date,_ = check_update_date()
date = str(date)

def minute_flag_check(date):
    path1 = flag_rootpath + str(date) + '/' + str(date) + '_%s_factors.success'%(kind.lower())    
    return os.path.exists(path1) 
    
    
flag_path = flag_rootpath + str(date) + '/'
if not os.path.exists(flag_path):
    os.makedirs(flag_path)
flag_path_start = flag_path + str(date) + '_%s_zscore.start' % str.lower(kind)
with open(flag_path_start,'w') as file:
    pass 

print('------wait minute flag')
while True:
    if minute_flag_check(date):
        break
    time.sleep(60)
print('flag check finished!')


path ='/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/%s_nonlinear/'%kind.upper()
path_new = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/%s_nonlinear_zscore/'%kind.upper()
path_diff_new = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/%s_nonlinear_diff_zscore/'%kind.upper()
for item in ['minute_norm/', 'minute_raw/']:
    if not os.path.exists(path_new + item):
        print('ZSCORE DOES NOT EXIST')
        os.makedirs(path_new + item)
    if not os.path.exists(path_diff_new + item):
        os.makedirs(path_diff_new + item)
        print('DIFF ZSCORE DOES NOT EXIST')


roll_win  = 60*240

def calc_ts_norm(ts_dat,roll_win=20,norm_type='zscore',min_pct=0.9):
    if len(ts_dat)<roll_win:
        print ('calc_ts_pct error: ts len too short: %d/%d'%(len(ts_dat),roll_win))
        raise Exception
    min_periods = int(min_pct*roll_win)

    if norm_type == 'min_max':
        ts_max =  ts_dat.rolling(roll_win,min_periods=min_periods).max()
        ts_min =  ts_dat.rolling(roll_win,min_periods=min_periods).min()
        ts_norm = (ts_dat-ts_min)/(ts_max - ts_min)
    elif norm_type == 'zscore':
        ts_mean =  ts_dat.rolling(roll_win,min_periods=min_periods).mean()
        ts_std =  ts_dat.rolling(roll_win,min_periods=min_periods).std()
        ts_norm = (ts_dat - ts_mean)/ts_std
    return ts_norm


def read_nl(item):
    temp_raw = pd.read_hdf(path+'minute_raw/'+item)
    #temp_raw.loc['20200203'] = np.nan
    factor_name = temp_raw.columns[0] + '_zscore'
    temp_raw.columns = [factor_name]
    temp_norm = calc_ts_norm(temp_raw, roll_win, norm_type = 'zscore', min_pct = 0.95)
    
    factor_raw_path = path_new + 'minute_raw/' + factor_name + '.h5'
    factor_norm_path = path_new + 'minute_norm/' + factor_name + '.h5'

    temp_raw.to_hdf(factor_raw_path, key='minute_data')
    temp_norm.to_hdf(factor_norm_path, key='minute_data')

with Pool(24) as pool:
     hholder_nl = pool.map(read_nl, os.listdir(path + 'minute_raw/'))
        


def read_diff_nl(item):
    temp_raw = pd.read_hdf(path+'minute_raw/'+item)
    #temp_raw.loc['20200203'] = np.nan
    factor_name = temp_raw.columns[0] + '_diff_zscore'
    temp_raw.columns = [factor_name]
    temp_norm = calc_ts_norm(temp_raw.diff(), roll_win, norm_type = 'zscore', min_pct = 0.95)
    
    factor_raw_path = path_diff_new + 'minute_raw/' + factor_name + '.h5'
    factor_norm_path = path_diff_new + 'minute_norm/' + factor_name + '.h5'
    
    if ('position_im_diff_zscore' in factor_raw_path) or ('position_diff_zscore' in factor_raw_path):
        pass
    else:
        temp_raw.to_hdf(factor_raw_path, key='minute_data')
        temp_norm.to_hdf(factor_norm_path, key='minute_data')

with Pool(24) as pool:
     hholder_nl = pool.map(read_diff_nl, os.listdir(path + 'minute_raw/'))
    
flag_path_success = flag_rootpath + str(date) + '/' + '%s_factors.success' % str.lower(kind)
with open(flag_path_success,'w') as file:
    pass



flag_path_start = flag_path + str(date) + '_%s_zscore.success' % str.lower(kind)
with open(flag_path_start,'w') as file:
    pass