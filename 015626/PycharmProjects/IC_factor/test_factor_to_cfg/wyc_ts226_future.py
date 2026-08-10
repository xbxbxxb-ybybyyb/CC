from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts226_future(FactorGenerator):
    def __init__(self):

        required_columns=['close_ih']
        lookback_bars=2000
        super(wyc_ts226_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        columnname = self.__class__.__name__
        N = 6
        N1 = 4
        N2 = 8
        MTM = df['close_ih'] - delay(df['close_ih'], 1)
        MTMMA = sma(MTM, N, 1)
        DIF = ts_mean(delay(MTMMA, 1), N1) - ts_mean(delay(MTMMA, 1), N2)
        factor = sma(DIF, 40, 1)
        factor = ts_rank_bk(factor, 20)
        factor = -1 * ts_mean(factor, 40)

        return factor