import sys
sys.path.insert(4, './utils')
from factor_generator import FactorGenerator
from factor_generator_complex import FactorGeneratorComplex
import os
import pandas as pd
from multiprocessing import Pool
from multifactor.data.utils import *
import multifactor.utility.dt as udt
import gc
import os, importlib
import datetime
import warnings
warnings.filterwarnings('ignore')

fs = [f for f in os.listdir('./new_submit/ic_new_submit/ic_20201118') if f.endswith('.py')]

for f in fs:
    importlib.import_module(f[:-3])
        
if __name__ == '__main__':
    prev_date = 20130101
    start_date = 20130201
    end_date = 20200331
    rlist = []
    
    FactorGeneratorComplex().prepare_hot_data(prev_date,end_date,use_cache = False, save_cache = False, ticker='IC.CFE', datakind = 'insample')
    subclass_list_cfg = FactorGeneratorComplex.__subclasses__()
#    for subcls in subclass_list_cfg:
#        print(subcls().__class__.__name__)
#        rlist.append(subcls().__callback__(start_date,end_date))
#        gc.collect()
        
    FactorGenerator().prepare_hot_data(prev_date,end_date, ticker = 'IC.CFE', datakind='insample')
    subclass_list = FactorGenerator.__subclasses__()
#    for subcls in subclass_list:
#        print(subcls().__class__.__name__)
#        rlist.append(subcls().__callback__(start_date,end_date))
#        gc.collect()


#    pd.DataFrame({'factorname':rlist}).to_csv('/data/user/015626/data/share/alpha/CHINA_FUTURES/MINUTE/factor_list/ic_submit_20201118.csv')


    print('factor count: ',len(subclass_list + subclass_list_cfg))
    
    def get_factors(subcls):
        print(subcls().__class__.__name__)
        return subcls().__callback__(start_date,end_date)
        
    nowlist = [x[:-3] for x in os.listdir('/data/user/015626/data/share/alpha/CHINA_FUTURES/MINUTE/IF_newsubmit1118/')]
    for x in (subclass_list + subclass_list_cfg):
        if x().__class__.__name__ in nowlist:
            continue
        else:
            get_factors(x)
#    with Pool(processes=20) as pool:
#        pool.map(get_factors, subclass_list + subclass_list_cfg)
        
    prev_date = 20200101
    start_date = 20200201
    end_date = 20201201
    
    
    FactorGeneratorComplex().prepare_hot_data(prev_date,end_date,use_cache = False, save_cache = False, ticker='IC.CFE', datakind = 'outsample')
    subclass_list_cfg = FactorGeneratorComplex.__subclasses__()
        
    FactorGenerator().prepare_hot_data(prev_date,end_date, ticker = 'IC.CFE', datakind='outsample')
    subclass_list = FactorGenerator.__subclasses__()
    
    print('factor count outsample: ',len(subclass_list + subclass_list_cfg))
    
#    with Pool(processes=20) as pool:
#        pool.map(get_factors, subclass_list + subclass_list_cfg)
    for x in (subclass_list + subclass_list_cfg):
        get_factors(x)
 
