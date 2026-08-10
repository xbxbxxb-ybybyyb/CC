from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts129_future(FactorGenerator):
    def __init__(self):

        required_columns=['close_if','volume_if']
        lookback_bars=2000
        super(wyc_ts129_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        N = 10
        key = 'close_if'
        factor = -1 * (df[key] - delay(df[key], N)) / delay(df[key], N) * df['volume_if']
        factor = ts_rank_bk(factor, 45)
        factor = ts_mean(factor, 45)

        return factor