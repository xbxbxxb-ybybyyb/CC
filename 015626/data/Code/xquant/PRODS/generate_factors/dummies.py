kind = 'dummies'
dtype = 'Future'
data_start_date = '20151101'
factor_start_date = '20151201'
end_date = '20210930'
norm_start_date = '20160101'

save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/%s/' % kind

factor_path = '/data/user/015626/data/share/Code/git_space/futures-factors-2/%s_factors' % str.lower(kind)

import sys
sys.path.insert(4,'/data/user/015626/data/share/Code/git_space/futures-factor-framework/factor_framework/')
sys.path.insert(4,factor_path)
sys.path.insert(4,'/data/user/015626/data/share/Code/git_space/futures-factors-2/utils')
import pandas as pd
import numpy as np
from future_factor import FutureFactor
from data_player import DataPlayer
from data_center import DataCenter
from multifactor.IO import IO
import multifactor.utility.dt as udt
from task_runner import TaskRunner
from future_factor import FutureFactor
import datetime
from function_tools import *
from scipy.stats import skew
import os, importlib
import time
ts = TaskRunner(save_factor=True, factor_root_path=save_path)

fs = [f for f in os.listdir(factor_path) if f.endswith('.py')]
for f in fs:
    importlib.import_module(f[:-3])
    
flist = FutureFactor.__subclasses__()

rdf = pd.DataFrame()
future_data_dict = {}
stock_data_dict = {}
future_factor_list = []
stock_factor_list = []
for f in flist:
    if f.data_type == 'Future':
        future_factor_list.append(f)
    else:
        stock_factor_list.append(f)
    
    factor_name = str(f).split("'")[1].split('.')[-1]
    rdf.loc[factor_name,'data_type'] = f.data_type
    rdf.loc[factor_name,'instrument_type'] = f.instrument_type
    rdf.loc[factor_name,'normalize_size'] = f.normalize_size
    rdf.loc[factor_name,'normalize_type'] = f.normalize_type
    rdf.loc[factor_name,'num_range'] = f.num_range
    rdf.loc[factor_name,'handle_preadj'] = f.handle_preadj
    rdf.loc[factor_name,'days_past'] = f.days_past
    rdf.loc[factor_name,'data_dict'] = str(f.data_dict)
# rdf.to_csv('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/material/IF_factor_details.csv')

class_list = future_factor_list if dtype == 'Future' else stock_factor_list
for c in class_list:
    try:
        factor_name = str(c).split("'")[1].split('.')[-1]
        if os.path.exists(os.path.join(save_path,'minute_norm',factor_name+'.h5')):
            continue
        print(factor_name)
        dc = DataCenter(variety = kind, data_type= dtype, instrument_type=c.instrument_type, data_dict = c.data_dict, 
                    start_date = data_start_date, end_date = end_date, days_past = c.days_past)
        stime = time.time()
        f = ts.run_factor_multi_day(factor = c(), variety = kind, data_center = dc, start_date = factor_start_date, end_date = end_date, ncore=24)
        etime = time.time()
        usetime = round((etime - stime)/60,3)
#        realfactor = pd.read_hdf(os.path.join('/data/user/015626/data/share/alpha/CHINA_FUTURES/MINUTE/factor_list/%s_all_1456/' % kind, factor_name + '.h5'))
#        realfactor = realfactor.loc[norm_start_date:'20200701']
#        tdf = realfactor.add_suffix('_real').join(f[1], how = 'inner')
#        corr = round(tdf[factor_name].corr(tdf[factor_name + '_real']),6)
        with open(os.path.join(save_path, '%s_%s.txt' % (kind,dtype)), 'a') as file:
            file.write('%s %s' % (factor_name, str(usetime)) + '\r\n')
#        if corr < 0.99:
#            print('!!!!!!!!!!!!!!!!!!!!')
        print('%s %s' % (factor_name, str(usetime)))
    except Exception as e:
        print(factor_name, e)
        with open(os.path.join(save_path, '%s_%s_wrong.txt' % (kind,dtype)), 'a') as file:
            file.write(factor_name + '#' + str(e) + '\r\n')
        continue