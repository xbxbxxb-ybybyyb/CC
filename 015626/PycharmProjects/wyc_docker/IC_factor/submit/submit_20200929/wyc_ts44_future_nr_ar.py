from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts44_future_nr_ar(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['volume' + suffix,'close' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts44_future_nr_ar, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        temp1 = df['volume' + suffix].copy(deep = True)
        con2 = df['close' + suffix]<delay(df['close' + suffix],1)
        temp1[con2] = -1 * df['volume' + suffix]
        factor = ts_sum(temp1,20)
        factor = ts_mean(factor, 20)

        factor = rolling_normalize(factor, 5 * 242)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        ar = (2 * a.rank(axis=1, pct=True) - 1)
        factor = factor * ar
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 20)
        factor = ts_mean(factor, 200)
        factor = rolling_normalize(factor, 5 * 242)
        factor.columns = [columnname]

        return factor
