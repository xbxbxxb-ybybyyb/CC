from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np

class wyc_ts207_future(FactorGenerator):
    def __init__(self):

        required_columns=['close_ih']
        lookback_bars=2000
        super(wyc_ts207_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        N = 10
        latefix = '_ih'
        factor = (sma(sma(sma(log(df['close' + latefix]), N, 2), N, 2), N, 2) - delay(
            sma(sma(sma(log(df['close' + latefix]), N, 2), N, 2), N, 2), 1)) / delay(
            sma(sma(sma(log(df['close' + latefix]), N, 2), N, 2), N, 2), 1)
        factor = ts_mean(-1 * factor, 10)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor < 0] = np.nan

        return factor