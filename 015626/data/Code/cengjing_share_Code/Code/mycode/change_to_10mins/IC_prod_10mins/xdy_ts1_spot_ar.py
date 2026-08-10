from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts1_spot_ar(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['high' + suffix, 'close' + suffix,'amount' + suffix, 'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts1_spot_ar, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        high = df['high' + suffix]
        close = df['close' + suffix]
        high[abs(high) < 1e-8] = np.nan
        gain_high_60 = high / high.shift(30) - 1
        h_c = close / high - 1
        a = ts_mean(h_c, 30)
        a[abs(a) < 1e-8] = np.nan
        factor = gain_high_60
        # factor = ts_sum(gain_high_60 / a, 10)
        # factor = ts_mean(factor, 10) * -1

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        ar = (2 * a.rank(axis=1, pct=True) - 1)
        factor = factor * ar
        factor = factor.sum(axis=1).to_frame()

        # factor = ts_rank(factor, 50)
        # factor = ts_mean(factor, 200)
        factor = ts_rank(factor, 3 * 237)
        
        factor.columns = [columnname]

        return factor