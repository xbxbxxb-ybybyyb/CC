from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts50_future_nr_cr(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix, 'stk_index_corr' + suffix]
        lookback_bars=2000
        super(wyc_ts50_future_nr_cr, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        returns = df['close' + suffix].pct_change(fill_method=None)
        N = 20
        factor = ts_sum((returns>0),N)
        factor = ts_mean(factor, N)
        factor = ts_rank_bk(factor, 5 * 242)

        factor = rolling_normalize(factor, 5 * 242)

        cr = (2 * df['stk_index_corr' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * cr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 300)
        factor = ts_mean(factor, 60)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]
        return factor