from factor_generator import FactorGenerator
from operators import *
import pandas as pd
import numpy as np
class wyc_ts44_future(FactorGenerator):
    def __init__(self):

        required_columns=['volume','close']
        lookback_bars=2000
        super(wyc_ts44_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        
        temp1 = df.volume.copy(deep = True)
        con1 = df.close>delay(df.close,1)
        con2 = df.close<delay(df.close,1)
        temp1[con2] = -1 * df.volume
        factor = ts_sum(temp1,20)
        factor = mean(factor, 20)

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
