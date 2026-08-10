from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts25_future_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_if']
        lookback_bars=2000
        super(wyc_ts25_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = mean(df.close_if, 50) / df.close_if
        factor = ts_rank_bk(factor, 5 * 242)
        factor = -1 * ts_mean(factor, 30)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor