from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts37_future(FactorGenerator):
    def __init__(self):
        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts37_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        factor = -1 * sma(((df['close']-ts_mean(df['close'],20))/ts_mean(df['close'],20) - delay((df['close'] - ts_mean(df['close'],20))/ts_mean(df['close'],20),6)),12,1)

        factor = ts_rank_bk(factor, 40)
        factor = ts_mean(factor, 50)

        return factor