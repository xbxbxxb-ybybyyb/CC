from factor_generator import FactorGenerator
from operators import *
import pandas as pd
import numpy as np
class wyc_ts15_future(FactorGenerator):
    def __init__(self):
        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts15_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        idx = df.index
        df = df.loc[~((idx.hour==9) & (idx.minute < 30))]
        df = df.sort_index()
        
        inner = (((delay(df['close'], 20) - delay(df['close'], 10)) / 10) - ((delay(df['close'], 10) - df['close']) / 10))
        factor = ts_rank(-1 * inner, 20)
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