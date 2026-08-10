from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts30_future_nr_cr(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'stk_index_corr' + suffix]
        lookback_bars=2000
        super(wyc_ts30_future_nr_cr, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        m = 30
        p1 = 20
        p2 = 40
        RC = df['close' + suffix] / delay(df['close' + suffix], 1)
        ARC1 = sma(delay(RC, 1), m, 1)
        DIF = ts_mean(delay(ARC1, 1), p1) - ts_mean(delay(ARC1, 1), p2)
        RCCD = sma(DIF, m, 1)
        factor = -1 * RCCD
        factor = ts_rank_bk(factor, 20)
        factor = ts_mean(factor, 60)

        factor = rolling_normalize(factor, 5 * 242)

        cr = (2 * df['stk_index_corr' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * cr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 20)
        factor = ts_mean(factor, 60)
        factor = rolling_normalize(factor, 5 * 242)
        factor.columns = [columnname]

        return factor
