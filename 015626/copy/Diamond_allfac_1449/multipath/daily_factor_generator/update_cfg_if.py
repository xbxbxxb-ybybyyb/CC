import sys
sys.path.insert(4, '/data/user/017024/overnight_factors/factors/overnight_prod_20210127_76/if/')
sys.path.insert(4, './operators/')
sys.path.insert(4, './utils/')

import os
import time
import importlib
import datetime as dt
import warnings
warnings.filterwarnings('ignore')

from factor_generator_complex import FactorGeneratorComplex
from utils.date_helper import *





ticker = 'IF.CFE'

if ticker == 'IC.CFE':
    fs = [f for f in os.listdir('/data/user/017024/overnight_factors/factors/overnight_prod_20210127_76/if/') if f.endswith('.py') & ~(f.split('.')[0].endswith('_if')|f.split('.')[0].endswith('_IF'))]
elif ticker == 'IF.CFE':
    fs = [f for f in os.listdir('/data/user/017024/overnight_factors/factors/overnight_prod_20210127_76/if/') if f.endswith('.py') & (f.split('.')[0].endswith('_if')|f.split('.')[0].endswith('_IF'))]

for f in fs:
    importlib.import_module(f[:-3])
        


if __name__ == '__main__':
    start_date, end_date, _ = check_update_date()
    report_flag_date = end_date
    prev_date = 20200101
    
    print(prev_date, start_date, end_date)
    
    def minute_flag_check(date):
        path1 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_IF_cfg_and_mask.success'
        path2 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_spot_minute.success'
        path3 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_tick_to_minute_future_data_and_mask.success'
        path4 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_cfg_hf.success'
        path5 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_overnight_dailydata.success'
        return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4) and os.path.exists(path5)
    
    flag_root = '/data/user/017024/data/flag/' + str(end_date) + '/'
    if not os.path.exists(flag_root):
        os.makedirs(flag_root)
    flag_path_start = flag_root + str(end_date) + '_overnight_factors_cfg_if.start'
    with open(flag_path_start,'w') as file:
        pass 

    print('------wait minute flag')
    while True:
        if minute_flag_check(end_date):
            break
        time.sleep(60)
    print('flag check finished!')



    print(dt.datetime.now())
    FactorGeneratorComplex().prepare_hot_data(prev_date, end_date, ticker=ticker, datakind = 'outsample')
    print(dt.datetime.now())
    subclass_list_cfg = FactorGeneratorComplex.__subclasses__()
    print('factor count outsample: ', len(subclass_list_cfg))
  
    for i, subcls in enumerate(subclass_list_cfg):
        print(i+1, subcls().__class__.__name__, dt.datetime.now())
        subcls(savepath='/data/user/017024/share/overnight/alpha/prod_76').__callback__(start_date, end_date)


        
    flag_path_success = flag_root + str(end_date) + '_overnight_factors_cfg_if.success'
    with open(flag_path_success,'w') as file:
        pass
        


