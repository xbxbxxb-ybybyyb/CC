from factor_generator import FactorGenerator
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
from multiprocessing import Pool


import os, importlib
fs = [f[:-3] for f in os.listdir('.') if f.endswith('.py')]
for f in fs:
    importlib.import_module(f)

if __name__ == '__main__':
    startdate, enddate = 20170101,20200801

    FactorGenerator().prepare_hot_data(startdate, enddate,future_kind = 'contract_main', ticker = 'IC.CFE')

    subclass_list = FactorGenerator.__subclasses__()

    def get_factors(subclass):
        print(subclass().__class__.__name__)
        subclass().__callback__(startdate, enddate)

    with Pool(processes=16) as pool:
        pool.map(get_factors, subclass_list)

    # for subclass in FactorGenerator.__subclasses__():
    #     print(subclass().__class__.__name__)
    #     inst = subclass()
    #     df = inst.__callback__(startdate, enddate)

