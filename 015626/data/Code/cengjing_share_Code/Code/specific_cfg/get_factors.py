from factor_generator import FactorGenerator
import warnings
warnings.filterwarnings('ignore')
from multiprocessing import Pool

import os, importlib
fs = [f[:-3] for f in os.listdir('.') if f.endswith('.py')]
for f in fs:
    if 'xdy' in f or 'wyc' in f:
        importlib.import_module(f)

if __name__ == '__main__':


    FactorGenerator().prepare_hot_data()

    subclass_list1 = FactorGenerator.__subclasses__()
    subclass_list = []
    spath = '/data/user/015626/data/share/factor/1min/IC_factors/jiemian/mid_variable_20200928/'
    nowfile = os.listdir(spath)
    nowfilelist = [x[:-7] for x in nowfile]
    for x in subclass_list1:
        if not x().__class__.__name__ in nowfilelist:
            subclass_list.append(x)
    print(len(subclass_list))

    def get_factors(subclass):
        print(subclass().__class__.__name__)
        subclass().__callback__()

    with Pool(processes=24) as pool:
        pool.map(get_factors, subclass_list)

    # for subclass in FactorGenerator.__subclasses__():
    # for subclass in subclass_list:
    #     print(subclass().__class__.__name__)
    #     inst = subclass()
    #     inst.__callback__()

