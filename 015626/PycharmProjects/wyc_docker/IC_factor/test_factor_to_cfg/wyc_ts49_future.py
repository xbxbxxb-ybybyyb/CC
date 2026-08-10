from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts49_future(FactorGenerator):
    def __init__(self):

        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts49_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        con1 = ((delta((ts_sum(df['close'], 100) / 100), 100) / delay(df['close'], 100)) <= 0.05)
        temp1 = df['close'].copy(deep = True)
        temp1[con1] = (df['close'] - ts_min(df['close'], 200))
        temp1[~con1] = delta(df['close'], 10)
        factor = temp1
        factor = ts_rank_bk(factor, 50)
        factor = ts_mean(factor, 50)

        return factor