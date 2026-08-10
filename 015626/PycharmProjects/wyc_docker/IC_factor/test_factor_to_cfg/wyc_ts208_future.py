from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts208_future(FactorGenerator):
    def __init__(self):
        required_columns=['close_ih']
        lookback_bars=2000
        super(wyc_ts208_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        key = 'close_ih'
        factor = pd.DataFrame(np.where(df[key] - delay(df[key], 1) < 0, abs(df[key] - delay(df[key], 1)), 0),
                              index=df[key].index, columns=df[key].columns)
        factor = ts_sum(factor, 12)
        factor = ts_rank_bk(factor, 20)
        factor = ts_mean(factor, 100)

        return factor