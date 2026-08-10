from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts49_spot(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts49_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        con1 = ((delta((ts_sum(df.close_spot, 100) / 100), 100) / delay(df.close_spot, 100)) <= 0.05)
        temp1 = df.close_spot.copy(deep = True)
        temp1[con1] = (df.close_spot - ts_min(df.close_spot, 100))
        temp1[~con1] = delta(df.close_spot, 10)
        factor = temp1
        factor = ts_rank(factor, 100)
        factor = mean(factor, 242)

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