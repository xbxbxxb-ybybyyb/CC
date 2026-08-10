from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts29_future_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_if','volume_if']
        lookback_bars=2000
        super(wyc_ts29_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        N = 20
        factor = (df.close_if - delay(df.close_if, N)) / delay(df.close_if, N) * df.volume_if
        factor = ts_rank_bk(factor, 2 * 242)
        factor = ts_mean(factor, 40)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor >= 0.5] = np.nan

        return factor