import sys
sys.path.insert(4, '/data/user/017024/overnight_factors/factors/Diamond_2_0_hf/')
sys.path.insert(4, './operators/')
sys.path.insert(4, './utils/')


import os
import importlib
import datetime as dt
from factor_generator_complex import FactorGeneratorComplex
import warnings
warnings.filterwarnings('ignore')


ticker = 'IC.CFE'
fs = [f for f in os.listdir('/data/user/017024/overnight_factors/factors/Diamond_2_0_hf/') if f.endswith('.py')]    
for f in fs:
    importlib.import_module(f[:-3])


if __name__ == '__main__':
   
    prev_date = 20151001
    start_date = 20160101
    end_date = 20200331
    
    print(dt.datetime.now())
    FactorGeneratorComplex().prepare_hot_data(prev_date, end_date, ticker=ticker, datakind = 'insample')
    print(dt.datetime.now())
    subclass_list_cfg = FactorGeneratorComplex.__subclasses__()
    print('factor count: ', len(subclass_list_cfg))
        
    for i, subcls in enumerate(subclass_list_cfg):
        print(i+1, subcls().__class__.__name__, dt.datetime.now())
        subcls(savepath='/data/user/017024/share/overnight/alpha/Diamond_2_0_20210713/').__callback__(start_date, end_date)
     
    
    prev_date = 20200201
    start_date = 20200401
    end_date = 20211231
    
    print(dt.datetime.now())
    FactorGeneratorComplex().prepare_hot_data(prev_date, end_date, ticker=ticker, datakind = 'outsample')
    print(dt.datetime.now())
    subclass_list_cfg = FactorGeneratorComplex.__subclasses__()
    print('factor count outsample: ', len(subclass_list_cfg))
  
    for i, subcls in enumerate(subclass_list_cfg):
        print(i+1, subcls().__class__.__name__, dt.datetime.now())
        subcls(savepath='/data/user/017024/share/overnight/alpha/Diamond_2_0_20210713/').__callback__(start_date, end_date)


    # prev_date = 20130101
    # start_date = 20130201
    # end_date = 20150630
        
    # print(dt.datetime.now())
    # FactorGeneratorComplex().prepare_hot_data(prev_date, end_date, use_cache = False, save_cache = False, ticker=ticker, datakind = 'insample_ago')
    # print(dt.datetime.now())
    # subclass_list_cfg = FactorGeneratorComplex.__subclasses__()
    # print('factor count outsample: ', len(subclass_list_cfg))
  
    # for i, subcls in enumerate(subclass_list_cfg):
        # print(i+1, subcls().__class__.__name__)
        # subcls().__callback__(start_date, end_date)

