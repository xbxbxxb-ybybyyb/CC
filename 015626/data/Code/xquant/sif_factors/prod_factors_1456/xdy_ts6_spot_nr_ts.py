from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts6_spot_nr_ts(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts6_spot_nr_ts, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        close = df['close' + suffix]
        gain_close_30 = ts_gain(close, 30)
        factor = ts_levelchange(gain_close_30, 20)
        factor = ts_mean(factor, 110)

        factor = rolling_norm(factor, 5 * 242)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        factor = factor * t
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 20)
        factor = ts_mean(factor, 200)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        # factor[factor > 0.2] = 0

        return factor