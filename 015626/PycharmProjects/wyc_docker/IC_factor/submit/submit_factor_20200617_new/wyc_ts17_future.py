from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts17_future(FactorGenerator):
    def __init__(self):
        required_columns=['close','low','volume']
        lookback_bars=2000
        super(wyc_ts17_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        
        inner = (df.close - ts_min(df.low, 12))
        factor = correlation(ts_rank(inner, 10), ts_rank(df.volume, 10),6)
        factor = mean(-1 * factor, 20)

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