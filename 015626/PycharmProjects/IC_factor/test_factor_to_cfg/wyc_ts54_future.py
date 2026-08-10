from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts54_future(FactorGenerator):
    def __init__(self):

        required_columns=['close','amount']
        lookback_bars=2000
        super(wyc_ts54_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        returns = df['close'].pct_change(fill_method=None)
        N = 10

        turnover = df['amount']
        s = turnover.rolling(N, min_periods=N // 2).std()
        f = returns.rolling(N, min_periods=N // 2).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = -1 * turnover.rolling(N, min_periods=N // 2).cov(returns) / (s * f)

        # factor = -1 * correlation(df.amount,returns,N).replace([np.inf,-np.inf],np.nan)
        factor = ts_rank_bk(factor, 15)
        factor = ts_mean(factor, 200)

        return factor