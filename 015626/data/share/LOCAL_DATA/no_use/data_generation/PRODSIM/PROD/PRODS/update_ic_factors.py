# 需注意获取IF  IC相应的代码文件，这里写得并不灵活,有两个地方
kind = 'IC'

import sys, os
sys.path.insert(1,'/data/user/016700/Data/Codes/git_space/futures-factor-framework/factor_framework/')
sys.path.insert(4,'/data/user/016700/Data/Codes/git_space/futures-factors-2/utils')
factor_rootpath = '/data/user/016700/Data/Codes/git_space/futures-factors-2/'
for folder in os.listdir(factor_rootpath):
    if kind == 'IF':
        if folder.startswith('if_'):
            sys.path.insert(4,os.path.join(factor_rootpath, folder))
    elif kind == 'IC':
        if not folder.startswith('if_'):
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
ifpy = glob.glob(factor_rootpath + 'if_*/*.py')
temppy = glob.glob(factor_rootpath + 'temp_*/*.py')
icpy = list(set(allpy) - set(ifpy) - set(temppy))

if kind == 'IF':
    fs = ifpy
elif kind == 'IC':
    fs = icpy#[:200]
    
for f in fs:
    importlib.import_module(f.split('/')[-1][:-3])
flist = FutureFactor.__subclasses__()

save_rootpath = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/'

_,date,_ = check_update_date()
date = str(date)
flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'

def get_save_path(factor_name):
    for x in fs:
        if x.split('/')[-1] == (factor_name + '.py'):
            factor_path = x
            break
    folder = factor_path.split('/')[-2]
    if 'dummies' in folder:
        folder = 'dummies'
    elif folder.startswith('ic'):
        folder = 'IC_' + folder.split('_')[-1]
    elif folder.startswith('if'):
        folder = 'IF_' + folder.split('_')[-1]
    raw_path = os.path.join(save_rootpath, folder, 'minute_raw')
    norm_path = os.path.join(save_rootpath, folder, 'minute_norm')
    if not os.path.exists(raw_path):
        os.makedirs(raw_path)
    if not os.path.exists(norm_path):
        os.makedirs(norm_path)
    return raw_path, norm_path
            
def minute_flag_check(date):
    path1 = flag_rootpath + str(date) + '/' + str(date) + '_CFG.success'
    path2 = flag_rootpath + str(date) + '/' + str(date) + '_INDUSTRY.success'
    path3 = flag_rootpath + str(date) + '/' + str(date) + '_INDEX.success'
    path4 = flag_rootpath + str(date) + '/' + str(date) + '_stock_index_future_universe.success'
    return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4)
 

flag_path = flag_rootpath + str(date) + '/'
if not os.path.exists(flag_path):
    os.makedirs(flag_path)
flag_path_start = flag_path + str(date) + '_%s_factors.start' % str.lower(kind)
with open(flag_path_start,'w') as file:
    pass 

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
    
flag_path_success = flag_path + str(date) + '_' + '%s_factors.success' % str.lower(kind)
with open(flag_path_success,'w') as file:
    pass
