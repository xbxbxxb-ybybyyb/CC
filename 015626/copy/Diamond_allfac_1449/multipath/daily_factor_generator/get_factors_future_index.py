import sys
sys.path.insert(4, '/data/user/017024/overnight/factors/prod_34/raw/')
sys.path.insert(4, './operators/')
sys.path.insert(4, './utils/')

import os
import importlib
import datetime as dt
from factor_generator import FactorGenerator
from factor_generator_xdy import FactorGeneratorXdy
import warnings
warnings.filterwarnings('ignore')


fs1 = [f for f in os.listdir('/data/user/017024/overnight/factors/prod_34/raw/') if f.endswith('.py')]
# fs2 = [f for f in os.listdir('/data/user/017024/overnight/factors/overnight_prod_20210127_76/if/') if f.endswith('.py')]
fs = fs1 # + fs2
for f in fs:
    importlib.import_module(f[:-3])


if __name__ == '__main__':
   
    prev_date = 20151001
    start_date = 20160101
    end_date = 20200831
    
    print(dt.datetime.now())
    FactorGenerator().prepare_hot_data(prev_date, end_date, datakind='insample')
    print(dt.datetime.now())
    subclass_list = FactorGenerator.__subclasses__()     
    print('factor count: ', len(subclass_list))
        
    for i, subcls in enumerate(subclass_list):
        print(i+1, subcls().__class__.__name__, dt.datetime.now())
        subcls(savepath='/data/user/017024/share/overnight/alpha/prod_34/raw/').__callback__(start_date, end_date)


    prev_date = 20200601
    start_date = 20200901
    end_date = 20211231
    
    print(dt.datetime.now())
    FactorGenerator().prepare_hot_data(prev_date, end_date, datakind='outsample')
    print(dt.datetime.now())
    subclass_list = FactorGenerator.__subclasses__()     

    print('factor count: ', len(subclass_list))
        
    for i, subcls in enumerate(subclass_list):
        print(i+1, subcls().__class__.__name__, dt.datetime.now())
        subcls(savepath='/data/user/017024/share/overnight/alpha/prod_34/raw/').__callback__(start_date, end_date)
    
            
    prev_date = 20120101
    start_date = 20160101
    end_date = 20211231
    
    print(dt.datetime.now())
    FactorGeneratorXdy().prepare_hot_data(prev_date, end_date)
    print(dt.datetime.now())
    subclass_list = FactorGeneratorXdy.__subclasses__()     

    print('factor count: ', len(subclass_list))
        
    for i, subcls in enumerate(subclass_list):
        print(i+1, subcls().__class__.__name__, dt.datetime.now())
        subcls(savepath='/data/user/017024/share/overnight/alpha/ic_prod').__callback__(start_date, end_date)
     

