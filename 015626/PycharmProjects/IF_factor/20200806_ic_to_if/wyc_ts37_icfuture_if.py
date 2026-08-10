from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts37_icfuture_if(FactorGenerator):
    def __init__(self):
        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts37_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = -1 * sma(((df.close - mean(df.close, 20)) / mean(df.close, 20) - delay(
            (df.close - mean(df.close, 20)) / mean(df.close, 20), 6)), 12, 1)

        factor = ts_rank_bk(factor, 40)
        factor = ts_mean(factor, 50)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)

        return factor