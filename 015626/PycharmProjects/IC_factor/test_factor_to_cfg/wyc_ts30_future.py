from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts30_future(FactorGenerator):
    def __init__(self):

        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts30_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        m = 30
        p1 = 20
        p2 = 40
        RC = df['close'] / delay(df['close'], 1)
        ARC1 = sma(delay(RC, 1), m, 1)
        DIF = ts_mean(delay(ARC1, 1), p1) - ts_mean(delay(ARC1, 1), p2)
        RCCD = sma(DIF, m, 1)
        factor = -1 * RCCD
        factor = ts_rank_bk(factor, 20)
        factor = ts_mean(factor, 60)

        return factor
