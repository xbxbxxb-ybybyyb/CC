from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np


class wyc_ts53_future(FactorGenerator):
    def __init__(self):

        required_columns=['close', 'volume', 'position', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts53_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        N = 10
        turnover = df['volume'] / df['position']
        returns = df['close'].pct_change(fill_method=None)
        s = turnover.rolling(N, min_periods=N//2).std()
        f = returns.rolling(N, min_periods=N//2).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = -1 * turnover.rolling(N, min_periods=N//2).cov(returns) / (s * f)

        # factor = -1 * correlation(turnover,returns,N).replace([np.inf,-np.inf],np.nan)
        factor = ts_rank_positive(factor, 15)
        factor = mean(factor, 100)
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = 0
        return factor