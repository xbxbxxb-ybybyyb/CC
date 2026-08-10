from factor_generator import FactorGenerator
import warnings
warnings.filterwarnings('ignore')
import pandas as pd


import os, importlib
fs = [f[:-3] for f in os.listdir('.') if f.endswith('.py')]
df = pd.DataFrame({'factorname':fs})
df.to_csv('/data/user/015626/data/share/factor/1min/xdy20200730/wyc_new_factors_20200730.csv', index = False)
exit()
for f in fs:
    if f[:-3] == 'wyc_icihif_spot':
        continue
    importlib.import_module(f[:-3])

if __name__ == '__main__':
    FactorGenerator(required_columns=['open', 'high', 'low', 'close', 'volume', 'amount', 'position', 'vwap', 'share','open_spot', 'high_spot', 'low_spot', 'close_spot', 'volume_spot', 'amt_spot','close_if','close_ih','volume_if','volume_ih','close_ic','volume_ic'],lookback_bars=500000000).prepare_hot_data()

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
