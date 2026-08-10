from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts6_spot(FactorGenerator):
    def __init__(self):
        required_columns=['volume_spot','high_spot','low_spot','close_spot']
        lookback_bars=2000
        super(wyc_ts6_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        
        N = 50
        factor = sma(df['volume_spot'] * ((df['close_spot'] - df['low_spot']) - (df['high_spot'] - df['close_spot'])) / (df['high_spot'] - df['low_spot']), N, 1)
        factor = ts_rank(factor, 100)
        factor = mean(factor, 160)

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
