from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
def rolling_normalize(df, x):
    def normalize(dd):
        a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
        b = (a - 0.5) * 2
        return b

    return df.rolling(x, min_periods=int(x / 2)).apply(normalize)

class wyc_ts7_future(FactorGenerator):
    def __init__(self):

        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts7_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        N = 15
        factor = (sma(sma(sma(log(df['close']), N, 2), N, 2), N, 2) - delay(
            sma(sma(sma(log(df['close']), N, 2), N, 2), N, 2), 1)) / delay(
            sma(sma(sma(log(df['close']), N, 2), N, 2), N, 2), 1)
        factor = mean(factor, 10)

        factor = factor.to_frame()    
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor<0]=np.nan
        return factor