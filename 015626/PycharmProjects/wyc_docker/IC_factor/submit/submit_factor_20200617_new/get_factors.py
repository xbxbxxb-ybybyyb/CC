from factor_generator import FactorGenerator
import warnings
warnings.filterwarnings('ignore')
from wyc_stix import wyc_stix
from multiprocessing import Pool

# import os, importlib
# fs = [f for f in os.listdir('.') if f.endswith('.py')]
# for f in fs:
#     importlib.import_module(f[:-3])

if __name__ == '__main__':
    FactorGenerator(required_columns=['open', 'high', 'low', 'close', 'volume', 'amount', 'position', 'vwap', 'share','open_spot', 'high_spot', 'low_spot', 'close_spot', 'volume_spot', 'amt_spot'],lookback_bars=500000000).prepare_hot_data()

    subclass_list = FactorGenerator.__subclasses__()

    # def get_factors(subclass):
    #     if 'spot' in subclass().__class__.__name__:
    #         pass
    #     print(subclass().__class__.__name__)
    #     inst = subclass()
    #     inst.__callback__()
    #
    # with Pool(processes=16) as pool:
    #     pool.map(get_factors, subclass_list)

    for subclass in FactorGenerator.__subclasses__():
        print(subclass().__class__.__name__)
        inst = subclass()
        df = inst.__callback__()
        print(df)
