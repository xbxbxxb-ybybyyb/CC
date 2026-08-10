from factor_generator import FactorGenerator
from operators import *
import pandas as pd
import numpy as np
class wyc_ts13_future(FactorGenerator):
    def __init__(self):
        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts13_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        factor = sma(mean(delay(sma(df['close'] - delay(df['close'], 1), 9, 1), 1), 12) - mean(
            delay(sma(df['close'] - delay(df['close'], 1), 9, 1), 1), 26), 10, 1)
        factor = mean(factor, 10)

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