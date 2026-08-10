from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts16_future(FactorGenerator):
    def __init__(self):
        required_columns=['close','low','volume']
        lookback_bars=2000
        super(wyc_ts16_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        
        returns = df.close.pct_change()
        factor = (((delta(ts_min(df.low, 50), 50)) * ts_rank(((ts_sum(returns, 240) - ts_sum(returns, 20)) / 220),
                                                               5)) * ts_rank(df.volume, 50))
        factor = ts_rank(factor, 242)
        factor = mean(factor, 100)

        factor = factor.to_frame()

        def rolling_normalize(df, x):
            def normalize(dd):
                a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
                b = (a - 0.5) * 2
                return b

            return df.rolling(x, min_periods=int(x / 2)).apply(normalize)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor