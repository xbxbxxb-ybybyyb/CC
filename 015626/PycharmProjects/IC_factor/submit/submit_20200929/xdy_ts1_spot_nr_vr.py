from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts1_spot_nr_vr(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['high' + suffix, 'close' + suffix,'stk_volatility' + suffix]
        lookback_bars=2000
        super(xdy_ts1_spot_nr_vr, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        high = df['high' + suffix]
        close = df['close' + suffix]
        gain_high_60 = high / high.shift(60) - 1
        h_c = close / high - 1
        a = ts_mean(h_c, 60)
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(gain_high_60 / a, 10)
        factor = ts_mean(factor, 10) * -1

        factor = rolling_normalize(factor, 5 * 242)

        vr = (2 * df['stk_volatility' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * vr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 50)
        factor = ts_mean(factor, 5)
        factor = rolling_normalize(factor, 5 * 242)
        factor.columns = [columnname]


        return factor