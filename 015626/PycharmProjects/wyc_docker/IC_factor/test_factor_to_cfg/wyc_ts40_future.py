from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts40_future(FactorGenerator):
    def __init__(self):

        required_columns=['close','volume','amount']
        lookback_bars=2000
        super(wyc_ts40_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        high = df['amount'] / df['volume']
        close = delay(df['close'], 20)
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        aa = high.rolling(20, min_periods=10).cov(close) / (s * f)


        factor = ((((ts_sum(df['close'], 20) / 20) - df['close'])) + aa)
        factor = ts_rank_bk(factor, 20)
        factor = ts_mean(factor, 100)

        return factor