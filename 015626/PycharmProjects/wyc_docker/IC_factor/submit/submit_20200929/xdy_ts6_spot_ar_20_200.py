from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts6_spot_ar_20_200(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts6_spot_ar_20_200, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        close = df['close' + suffix]
        gain_close_30 = ts_gain(close, 30)
        factor = ts_levelchange(gain_close_30, 20)
        factor = ts_mean(factor, 110)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        ar = (2 * a.rank(axis=1, pct=True) - 1)
        factor = factor * ar
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 20)
        factor = ts_mean(factor, 200)
        factor = rolling_normalize(factor, 5 * 242)
        factor.columns = [columnname]

        return factor