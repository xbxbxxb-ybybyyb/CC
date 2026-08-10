from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts24_spot_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot_if','high_spot_if','low_spot_if']
        lookback_bars=2000
        super(wyc_ts24_spot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        N = 35
        wmadf = mean(df.close_spot_if, N)
        long = ts_max(df.high_spot_if, N) - wmadf
        short = ts_min(df.low_spot_if, N) - wmadf
        factor = (long - short) / df.close_spot_if
        # factor = ts_rank_bk(factor, 82)
        factor = ts_mean(factor, 20)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 4 * 242)
        factor[factor <= -0.5] = np.nan
        return factor