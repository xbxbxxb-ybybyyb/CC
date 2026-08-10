from factor_generator import FactorGenerator
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
from multiprocessing import Pool


import os, importlib
fs = [f[:-3] for f in os.listdir('.') if f.endswith('.py')]
for f in fs:
    if ('cfg' in f) or ('CFG' in f) or f.startswith('factor'):
        continue
    importlib.import_module(f)

if __name__ == '__main__':
    # startdate, enddate = 20160101,20200901
    startdate, enddate = 20160101, 20200901

    FactorGenerator().prepare_hot_data(startdate, enddate,future_kind = 'contract_00', ticker = 'IC.CFE')

    subclass_list1 = FactorGenerator.__subclasses__()
    subclass_list = []
    spath = '/data/user/015626/data/share/factor/1min/IC_factors/tick_to_minute_wind_00_20200907/IC_prod_00/'
    nowfile = os.listdir(spath)
    nowfilelist = [x[:-3] for x in nowfile]
    for x in subclass_list1:
        if not x().__class__.__name__ in nowfilelist:
            subclass_list.append(x)
    print(len(subclass_list))

    def get_factors(subclass):
        # print(subclass().__class__.__name__)
        subclass().__callback__(startdate, enddate)

    with Pool(processes=16) as pool:
        pool.map(get_factors, subclass_list)

    # for subclass in FactorGenerator.__subclasses__():
    #     print(subclass().__class__.__name__)
    #     inst = subclass()
    #     df = inst.__callback__(startdate, enddate)

