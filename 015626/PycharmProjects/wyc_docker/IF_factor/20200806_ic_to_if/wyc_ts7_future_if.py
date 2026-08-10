from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np

class wyc_ts7_future_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_if']
        lookback_bars=2000
        super(wyc_ts7_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        N = 30
        factor = (sma(sma(sma(log(df['close_if']), N, 2), N, 2), N, 2) - delay(
            sma(sma(sma(log(df['close_if']), N, 2), N, 2), N, 2), 1)) / delay(
            sma(sma(sma(log(df['close_if']), N, 2), N, 2), N, 2), 1)
        factor = ts_mean(factor, 5)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 3 * 242)
        return factor