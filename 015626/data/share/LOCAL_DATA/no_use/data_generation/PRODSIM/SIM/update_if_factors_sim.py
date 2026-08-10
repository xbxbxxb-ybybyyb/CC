# 需注意获取IF  IC相应的代码文件，这里写得并不灵活,有两个地方
kind = 'IF'

flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS_sim/'

path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/if_features_new_181/'
path_new = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_zscore/'
path_diff_new = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_diff_zscore/'


import sys, os
sys.path.insert(1,'/data/group/800466/warehouse/test/alpha/framework_for_im/')
sys.path.insert(4,'/data/user/016700/Data/Codes/utils')
factor_rootpath = '/data/user/016700/data/space/'
for folder in os.listdir(factor_rootpath):
    if kind == 'IF':
        if folder.startswith('IF_') or folder.startswith('if_'):
            sys.path.insert(4,os.path.join(factor_rootpath, folder))
    elif kind == 'IH':
        if folder.startswith('IH_') or folder.startswith('ih_'):
            sys.path.insert(4,os.path.join(factor_rootpath, folder))
    
import pandas as pd
import numpy as np
from future_factor import FutureFactor
from data_player import DataPlayer
from data_center import DataCenter
from multifactor.IO import IO
import multifactor.utility.dt as udt
from task_runner import TaskRunner
from future_factor import FutureFactor
from scipy.stats import skew
import importlib
import time, datetime, glob
from multiprocessing import Pool
from multifactor.data.utils import *
allpy = glob.glob(factor_rootpath + '*/*.py')
ifpy = glob.glob(factor_rootpath + 'IF_*/*.py') + glob.glob(factor_rootpath + 'if_*/*.py')
temppy = glob.glob(factor_rootpath + 'temp_*/*.py')
icpy = list(set(allpy) - set(ifpy) - set(temppy))

if kind == 'IF':
    fs = ifpy
elif kind == 'IH':
    fs = icpy
    
for f in fs:
    importlib.import_module(f.split('/')[-1][:-3])
flist = FutureFactor.__subclasses__()

save_rootpath = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/'

_,date,_ = check_update_date()
date = str(date)


def get_save_path(factor_name):
    for x in fs:
        if x.split('/')[-1] == (factor_name + '.py'):
            factor_path = x
            break
    folder = factor_path.split('/')[-2]
    if 'dummies' in folder:
        folder = 'dummies'
    
    raw_path = os.path.join(save_rootpath, folder, 'minute_raw')
    norm_path = os.path.join(save_rootpath, folder, 'minute_norm')
    if not os.path.exists(raw_path):
        os.makedirs(raw_path)
    if not os.path.exists(norm_path):
        os.makedirs(norm_path)
    return raw_path, norm_path
            
def minute_flag_check(date):

    path4 = flag_rootpath + str(date) + '/' + str(date) + '_CFG.success'
    return os.path.exists(path4)
 

flag_path = flag_rootpath + str(date) + '/'

print('------wait minute flag')
while True:
    if minute_flag_check(date):
        break
    time.sleep(60)
print('flag check finished!')
       
for data_type in ['Future', 'IndexStock']:
    biggest_dayspast = 0
    finaldata_dict = {}
    for f in flist:
        if f.data_type != data_type:
            continue
        if f.days_past > biggest_dayspast:
            biggest_dayspast = f.days_past
        for key,value in f.data_dict.items():
            if key in finaldata_dict.keys():
                if key in ['Continuous_Data', 'Index_Id', 'Other_Future_Instrument', 'Other_Variety']:
                    for k,v in value.items():
                        if k in finaldata_dict[key].keys():
                            finaldata_dict[key][k] = list(set(finaldata_dict[key][k]) | set(v))
                        else:
                            finaldata_dict[key][k] = v
                elif key in ['Future_Data','Stock']:
                    finaldata_dict[key] = list(set(finaldata_dict[key]) | set(value))
            else:
                finaldata_dict[key] = value
            
    print('start datacenter')            
    data_start_date = udt.get_trading_day_offset(date,-1 * biggest_dayspast)[0].strftime('%Y%m%d')
    dc = DataCenter(variety = kind, data_type= data_type, instrument_type='recent', data_dict = finaldata_dict, 
                            start_date = data_start_date, end_date = date, days_past = biggest_dayspast)
    print('data center done')
   
    def get_factor(factor):
        if factor.data_type != data_type:
            return
        ts = TaskRunner(save_factor=False, factor_root_path=None)
        factor_name = str(factor).split("'")[1].split('.')[-1]
        normalize_size = factor.normalize_size
        normalize_type = factor.normalize_type
        raw = ts.run_factor_single_day(factor(),date,data_center=dc)
        raw_path, norm_path = get_save_path(factor_name)
        factor_raw_path = os.path.join(raw_path,'%s.h5' % factor_name)
        factor_norm_path = os.path.join(norm_path,'%s.h5' % factor_name)
        if os.path.exists(factor_raw_path):
            origin_value = pd.read_hdf(factor_raw_path).loc[:'%s000000'%date]
            raw = origin_value.append(raw)

        if normalize_size in [0,1]:
            norm = raw.copy()
            norm.to_hdf(factor_norm_path, key='minute_data')
        else:
            if len(raw) >= normalize_size:
                if factor.normalize_type == 'ts_rank':
                    norm = ts.ts_rank(raw, normalize_size)
                elif factor.normalize_type == 'rolling_norm':
                    norm = ts.rolling_norm(raw, normalize_size)
                norm.to_hdf(factor_norm_path, key='minute_data')
        raw.to_hdf(factor_raw_path, key='minute_data')
        del(ts)
        print(factor_name, 'done')

    with Pool(24) as pool:
        pool.map(get_factor, flist)


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
from operators_cc import *
import datetime
import warnings
warnings.filterwarnings('ignore')
import bottleneck as bk
import datetime
from multifactor.data.utils import *
from datetime import timedelta
from multiprocessing.pool import Pool
import matplotlib.pyplot as plt



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
    
    if ('position_if_diff_zscore' in factor_raw_path) or ('position_diff_zscore' in factor_raw_path):
        pass
    else:
        temp_raw.to_hdf(factor_raw_path, key='minute_data')
        temp_norm.to_hdf(factor_norm_path, key='minute_data')

with Pool(24) as pool:
     hholder_nl = pool.map(read_diff_nl, os.listdir(path + 'minute_raw/'))
    
    
flag_path_success = flag_rootpath + str(date) + '/' + '%s_factors.success' % str.lower(kind)
with open(flag_path_success,'w') as file:
    pass