from factor_generator import FactorGenerator
from operators import *
import pandas as pd
import numpy as np
class wyc_ts45_future(FactorGenerator):
    def __init__(self):

        required_columns=['volume','close']
        lookback_bars=2000
        super(wyc_ts45_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        factor =((ts_rank(((sign((df.close - delay(df.close, 1))) + sign((delay(df.close, 1) - delay(df.close, 2)))) +sign((delay(df.close, 2) - delay(df.close, 3)))),20)) * ts_sum(df.volume, 5)) / ts_sum(df.volume, 20)
        factor = ts_rank(-1 * factor, 20)
        factor = mean(factor, 20)
        factor = mean(factor, 15)

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