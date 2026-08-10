from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts6_spot_tr_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['close' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts6_spot_tr_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        close = df['close' + suffix]
        gain_close_30 = ts_gain(close, 30)
        factor = ts_levelchange(gain_close_30, 20)
        factor = ts_mean(factor, 110)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        tr = (2 * t.rank(axis=1, pct=True) - 1)
        factor = factor * tr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 300)
        factor = ts_mean(factor, 5)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        # factor[factor<0] = 0

        return factor