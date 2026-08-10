from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts1_spot_cr_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['high' + suffix, 'close' + suffix,'stk_index_corr' + suffix]
        lookback_bars=2000
        super(xdy_ts1_spot_cr_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        high = df['high' + suffix]
        close = df['close' + suffix]
        high[abs(high) < 1e-8] = np.nan
        gain_high_60 = high / high.shift(60) - 1
        h_c = close / high - 1
        a = ts_mean(h_c, 60)
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(gain_high_60 / a, 10)
        factor = ts_mean(factor, 10) * -1

        cr = (2 * df['stk_index_corr' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * cr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 150)
        factor = ts_mean(factor, 5)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor > 0] = 0


        return factor