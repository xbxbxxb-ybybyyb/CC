from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts207_spot(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot_ih']
        lookback_bars=2000
        super(wyc_ts207_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        N = 20
        latefix = '_ih'
        factor = (sma(sma(sma(log(df['close_spot' + latefix]), N, 2), N, 2), N, 2) - delay(
            sma(sma(sma(log(df['close_spot' + latefix]), N, 2), N, 2), N, 2), 1)) / delay(
            sma(sma(sma(log(df['close_spot' + latefix]), N, 2), N, 2), N, 2), 1)

        factor = ts_rank_bk(factor, 10)
        factor = ts_mean(-1 * factor, 40)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 7 * 242)
        factor[factor >= 0] = np.nan

        return factor