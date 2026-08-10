from factor_generator_complex import FactorGeneratorComplex
import warnings
warnings.filterwarnings('ignore')
from multiprocessing import Pool

import os, importlib
fs = [f for f in os.listdir('.') if f.endswith('.py')]
for f in fs:
    # if 'wyc' in f or 'xdy' in f:
    if 'wyc_ts6_future_nr_cr' in f:
        importlib.import_module(f[:-3])

if __name__ == '__main__':
    FactorGeneratorComplex(required_columns=['open_zz500', 'high_zz500', 'low_zz500', 'close_zz500','weight_zz500','volume_zz500','open', 'high', 'low', 'close', 'volume', 'amount',
                                             'position', 'vwap', 'share','open_spot', 'high_spot', 'low_spot',
                                             'close_spot', 'volume_spot', 'amt_spot','close_if','close_ih',
                                             'volume_if','volume_ih','close_ic','volume_ic'],
                           lookback_bars=500000000,
                           savepath='/data/user/015626/data/share/factor/1min/IC_factors/submit_test_20200904') \
                            .prepare_hot_data(20150101, 20210101)

    subclass_list1 = FactorGeneratorComplex.__subclasses__()
    subclass_list = []
    spath = '/data/user/015626/data/share/factor/1min/IC_factors/ts6_test_20201009/IC_prod/'
    if not os.path.exists(spath):
        os.makedirs(spath)
    nowfile = os.listdir(spath)
    nowfilelist = [x[:-3] for x in nowfile]
    for x in subclass_list1:
        if not x().__class__.__name__ in nowfilelist:
            subclass_list.append(x)
    print(len(subclass_list))

    for subclass in subclass_list:
        print(subclass().__class__.__name__)
        inst = subclass()
        inst.__callback__(20150101, 20210101)

    # def get_factors(subclass):
    #     print(subclass().__class__.__name__)
    #     inst = subclass()
    #     inst.__callback__(20160101, 20200101)
    #
    # with Pool(processes=24) as pool:
    #     pool.map(get_factors, subclass_list)

