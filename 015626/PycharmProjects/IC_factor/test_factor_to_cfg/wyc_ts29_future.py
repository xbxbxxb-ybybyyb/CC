from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts29_future(FactorGenerator):
    def __init__(self):

        required_columns=['close','volume']
        lookback_bars=2000
        super(wyc_ts29_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 10
        factor = -1 * (df['close'] - delay(df['close'], N)) / delay(df['close'],N) * df['volume']
        factor = ts_rank_bk(factor, 45)
        factor = ts_mean(factor, 45)

        return factor