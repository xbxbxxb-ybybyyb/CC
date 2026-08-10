from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts19_spot(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot','low_spot','high_spot','volume_spot']
        lookback_bars=2000
        super(wyc_ts19_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        factor = ts_sum(((df.close_spot-df.low_spot)-(df.high_spot-df.close_spot))/(df.high_spot-df.low_spot)*df.volume_spot,10)

        factor = ts_rank(factor, 242)
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