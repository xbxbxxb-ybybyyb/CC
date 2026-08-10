from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk


class wyc_ts19_future_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_if','low_if','high_if','volume_if']
        lookback_bars=2000
        super(wyc_ts19_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self,df):
        columnname = self.__class__.__name__

        factor = ts_sum(
            ((df.close_if - df.low_if) - (df.high_if - df.close_if)) / (df.high_if - df.low_if) * df.volume_if, 20)
        factor = ts_rank(factor, 240)
        factor = ts_mean(factor, 100)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 1200)
        factor[factor <= -0.5] = np.nan

        return factor