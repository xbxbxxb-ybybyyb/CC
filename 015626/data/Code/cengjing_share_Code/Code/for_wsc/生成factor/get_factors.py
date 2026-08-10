from factor_generator import FactorGenerator
import warnings
warnings.filterwarnings('ignore')
import pandas as pd


import os, importlib
fs = [f[:-3] for f in os.listdir('.') if f.endswith('.py')]
# df = pd.DataFrame({'factorname':fs})
# df.to_csv('/data/user/015626/data/share/factor/1min/xdy20200730/wyc_new_factors_20200730.csv', index = False)
# exit()
for f in fs:
    if f[:-3].startswith('wyc'):
        importlib.import_module(f)

if __name__ == '__main__':
    FactorGenerator(required_columns=['open', 'high', 'low', 'close', 'volume', 'amount', 'position', 'vwap', 'share','open_spot', 'high_spot', 'low_spot', 'close_spot', 'volume_spot', 'amt_spot',
                                      'open_ih', 'high_ih', 'low_ih', 'close_ih', 'volume_ih', 'amount_ih', 'position_ih', 'vwap_ih', 'share_ih',
                                      'open_spot_ih', 'high_spot_ih', 'low_spot_ih', 'close_spot_ih', 'volume_spot_ih', 'amt_spot_ih',
                                      'open_if', 'high_if', 'low_if', 'close_if', 'volume_if', 'amount_if', 'position_if', 'vwap_if', 'share_if','open_spot_if', 'high_spot_if', 'low_spot_if', 'close_spot_if', 'volume_spot_if', 'amt_spot_if'],lookback_bars=500000000).prepare_hot_data()

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
