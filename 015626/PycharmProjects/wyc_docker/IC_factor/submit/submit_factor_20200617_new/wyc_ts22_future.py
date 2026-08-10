from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts22_future(FactorGenerator):
    def __init__(self):
        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts22_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        
        N1 = 4
        N2 = 8
        N3 = 8
        Rn1 = (df.close - delay(df.close, N1)) / delay(df.close, N1) * 100
        Rn2 = (df.close - delay(df.close, N2)) / delay(df.close, N2) * 100
        RCn1n2 = (Rn1 + Rn2).to_frame()
        factor = wma(RCn1n2, N3)
        factor = ts_rank(factor, 242)
        factor = mean(factor, 242)

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
