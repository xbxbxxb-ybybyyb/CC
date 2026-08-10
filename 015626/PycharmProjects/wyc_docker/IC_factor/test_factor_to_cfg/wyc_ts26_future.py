from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts26_future(FactorGenerator):
    def __init__(self):

        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts26_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        
        N = 6
        N1 = 4
        N2 = 8
        MTM = df['close'] - delay(df['close'], 1);
        MTMMA = sma(MTM, N, 1);
        DIF = ts_mean(delay(MTMMA, 1), N1) - ts_mean(delay(MTMMA, 1), N2)
        factor = sma(DIF, 100, 1)
        factor = ts_rank_bk(factor, 242 * 2)
        factor = ts_mean(factor, 242)

        return factor