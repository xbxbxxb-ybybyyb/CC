from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts229_future(FactorGenerator):
    def __init__(self):

        required_columns=['close_ih','volume_ih']
        lookback_bars=2000
        super(wyc_ts229_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        N = 10
        key = 'close_ih'
        factor = -1 * (df[key] - delay(df[key], N)) / delay(df[key], N) * df['volume_ih']
        factor = ts_rank_bk(factor, 45)
        factor = ts_mean(factor, 45)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor