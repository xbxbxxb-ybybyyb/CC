from factor_generator_complex import FactorGeneratorComplex
import warnings
warnings.filterwarnings('ignore')

import os, importlib
fs = [f for f in os.listdir('.') if f.endswith('.py')]
for f in fs:
    if f[:-3] == 'wyc_icihif_spot':
        continue
    importlib.import_module(f[:-3])

if __name__ == '__main__':
    FactorGeneratorComplex(required_columns=['close_zz500','open', 'high', 'low', 'close', 'volume', 'amount',
                                             'position', 'vwap', 'share','open_spot', 'high_spot', 'low_spot',
                                             'close_spot', 'volume_spot', 'amt_spot','close_if','close_ih',
                                             'volume_if','volume_ih','close_ic','volume_ic'],
                           lookback_bars=500000000,
                           savepath='/data/user/015626/data/share/factor/1min/xdy20200730') \
                            .prepare_hot_data(20200101, 20200201)

    # subclass_list = FactorGeneratorComplex.__subclasses__()

    for subclass in FactorGeneratorComplex.__subclasses__():
        inst = subclass()
        inst.__callback__(20200101, 20200201)

