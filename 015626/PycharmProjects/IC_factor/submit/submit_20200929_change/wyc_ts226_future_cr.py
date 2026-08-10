from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts226_future_cr(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix, 'stk_index_corr' + suffix]
        lookback_bars=2000
        super(wyc_ts226_future_cr, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__
        N = 6
        N1 = 4
        N2 = 8
        MTM = df['close' + suffix] - delay(df['close' + suffix], 1)
        MTMMA = sma(MTM, N, 1)
        DIF = ts_mean(delay(MTMMA, 1), N1) - ts_mean(delay(MTMMA, 1), N2)
        factor = sma(DIF, 40, 1)
        factor = ts_rank_bk(factor, 20)
        factor = -1 * ts_mean(factor, 40)

        cr = (2 * df['stk_index_corr' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * cr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 300)
        factor = ts_mean(factor, 80)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        return factor