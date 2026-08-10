from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts27_future(FactorGenerator):
    def __init__(self):

        required_columns=['close','volume']
        lookback_bars=2000
        super(wyc_ts27_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        temp = df.close.copy()
        con1 = df.close > delay(df.close, 1)
        OBV = temp.copy()
        OBV[con1] = df.volume
        con2 = df.close < delay(df.close, 1)
        OBV[~con1 & con2] = -1 * df.volume
        OBV[~con1 & ~con2] = 0
        factor = -1 * ts_sum(OBV, 10)
        factor = ts_rank(factor, 20)
        factor = mean(factor, 60)

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