import sys
sys.path.insert(4, '/data/user/017024/share/overnight/factors/prod_26_new/')
sys.path.insert(4, './operators/')
sys.path.insert(4, './utils/')

import os
import time
import importlib
import datetime as dt
from multiprocessing import Pool
# from joblib import Parallel, delayed
import warnings
warnings.filterwarnings('ignore')

from factor_generator import FactorGenerator
from factor_generator_xdy import FactorGeneratorXdy
from factor_generator_complex import FactorGeneratorComplex
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from utils.date_helper import *




fs = [f for f in os.listdir('/data/user/017024/share/overnight/factors/prod_26_new/') if f.endswith('.py')]
for f in fs:
    importlib.import_module(f[:-3])
    


if __name__ == '__main__':
    start_date = end_date = int(dt.datetime.now().strftime("%Y%m%d")) - 1
    
    def minute_flag_check(date):
        path1 = os.path.join('/data/user/012245/warehouse/flags/', str(date), str(date)+'_CLOSURE.success')  # 徐博提供的指数和期货数据
        path2 = os.path.join('/data/user/017024/share/overnight/data/flag/', str(date), str(date)+'_cfg_afternoon.success')  # 下午的Wind成分股数据
        path3 = os.path.join('/data/user/015626/data/share/LOCAL_DATA/FLAG/', str(date), str(date)+'_IC_cfg_and_mask_noondata_for_overnight.success')  # 魏总提供的截止中午的zz500成分股数据
        path4 = os.path.join('/data/user/015626/data/share/LOCAL_DATA/FLAG/', str(date), str(date)+'_IF_cfg_and_mask_noondata_for_overnight.success')  # 魏总提供的截止中午的hs300成分股数据
        return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4)

    print('------wait minute flag')
    while True:
        if minute_flag_check(end_date):
            break
        time.sleep(1)
    print('flag check finished!')
    

        
    
    prev_date = 20200101
    print(dt.datetime.now())
    print(prev_date, start_date, end_date)
    FactorGeneratorComplex().prepare_hot_data(prev_date, end_date)
    print(dt.datetime.now())
    subclass_list = FactorGeneratorComplex.__subclasses__()     
    print('factor count: ', len(subclass_list))
        
#    for i, subcls in enumerate(subclass_list):
#        print(i+1, subcls().__class__.__name__, dt.datetime.now())
#        subcls(savepath='/data/user/017024/share/overnight/alpha_intraday/prod_26_new').__callback__(start_date, end_date)
    def func1(subcls):
        print(subcls().__class__.__name__)
        subcls(savepath='/data/user/017024/share/overnight/alpha_intraday/prod_26_new').__callback__(start_date, end_date)
        return None
    
    print(dt.datetime.now())
    # Parallel(n_jobs=-1, max_nbytes='1G')(delayed(func1)(i) for i in subclass_list)
    with Pool(processes=16) as pool:
        pool.map(func1, subclass_list)
    print(dt.datetime.now())

        



