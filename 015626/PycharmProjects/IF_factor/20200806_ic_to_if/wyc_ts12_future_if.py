from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts12_future_if(FactorGenerator):
    def __init__(self):
        required_columns=['close_if']
        lookback_bars=2000
        super(wyc_ts12_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = (ts_mean(df['close_if'], 48) + ts_mean(df['close_if'], 6) + ts_mean(df['close_if'], 12) + ts_mean(
            df['close_if'], 24)) / 4
        factor = ts_rank_bk(factor, 10)
        factor = ts_mean(factor, 40)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor