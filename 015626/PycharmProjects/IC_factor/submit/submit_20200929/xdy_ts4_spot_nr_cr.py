from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts4_spot_nr_cr(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['high' + suffix,'stk_index_corr' + suffix]
        lookback_bars=2000
        super(xdy_ts4_spot_nr_cr, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        high = df['high' + suffix]
        factor = ts_position(high, 30)
        factor = -1 * factor.rolling(100, min_periods=20).skew()

        factor = rolling_normalize(factor, 5 * 242)

        cr = (2 * df['stk_index_corr' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * cr
        factor = factor.sum(axis=1).to_frame()

        factor = rolling_normalize(factor, 5 * 242)
        factor.columns = [columnname]

        return factor