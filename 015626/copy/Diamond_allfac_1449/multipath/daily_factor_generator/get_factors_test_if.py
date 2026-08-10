import sys
sys.path.insert(4, './daily_factor_generator/newly_submit/20210114_if')
sys.path.insert(4, './operators/')
sys.path.insert(4, './utils_wsc/')

import os
import importlib
import datetime as dt
import warnings
from factor_generator import FactorGenerator
from factor_generator_complex import FactorGeneratorComplex
warnings.filterwarnings('ignore')

fs = [f for f in os.listdir('./daily_factor_generator/newly_submit/20210114_if') if f.endswith('.py')]
for f in fs:
    importlib.import_module(f[:-3])

ticker = 'IF.CFE'

if __name__ == '__main__':
   
    prev_date = 20200101
    start_date = 20200201
    end_date = 20200731
    
    print(dt.datetime.now())
    FactorGenerator().prepare_hot_data(prev_date, end_date, use_cache = False, save_cache = False, ticker = ticker)
    print(dt.datetime.now())
    subclass_list = FactorGenerator.__subclasses__()
    
    print(dt.datetime.now())
    FactorGeneratorComplex().prepare_hot_data(prev_date, end_date, use_cache = False, save_cache = False, ticker=ticker, datakind = 'outsample')
    print(dt.datetime.now())
    subclass_list_cfg = FactorGeneratorComplex.__subclasses__()
      
    print('factor count: ', len(subclass_list + subclass_list_cfg))
        
    for i, subcls in enumerate(subclass_list + subclass_list_cfg):
        print(i+1, subcls().__class__.__name__)
        subcls(savepath = '/data/user/017024/data/IF_factors/overnight').__callback__(start_date, end_date)
     

