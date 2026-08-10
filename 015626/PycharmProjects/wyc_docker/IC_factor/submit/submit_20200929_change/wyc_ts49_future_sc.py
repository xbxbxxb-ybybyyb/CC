from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts49_future_sc(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix, 'stk_index_corr' + suffix]
        lookback_bars=2000
        super(wyc_ts49_future_sc, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        con1 = ((delta((ts_sum(df['close' + suffix], 100) / 100), 100) / delay(df['close' + suffix], 100)) <= 0.05)
        temp1 = df['close' + suffix].copy(deep = True)
        temp1[con1] = (df['close' + suffix] - ts_min(df['close' + suffix], 200))
        temp1[~con1] = delta(df['close' + suffix], 10)
        factor = temp1
        factor = ts_rank_bk(factor, 50)
        factor = ts_mean(factor, 50)

        factor = factor * df['stk_index_corr' + suffix]
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        return factor