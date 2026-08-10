from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts37_spot(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts37_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        factor = -1 * sma(((df.close_spot-mean(df.close_spot,25))/mean(df.close_spot,25) - delay((df.close_spot - mean(df.close_spot,25))/mean(df.close_spot,25),6)),12,5)

        factor = ts_rank(factor, 25)
        factor = mean(factor, 50)

        factor = factor.to_frame()
        factor.iloc[:, 0] = factor.iloc[:, 0].rolling(5, min_periods = 2).mean()
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