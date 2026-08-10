from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts8_future(FactorGenerator):
    def __init__(self):
        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts8_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        factor = pd.DataFrame(
            np.where(df['close'] - delay(df['close'], 1) < 0, abs(df['close'] - delay(df['close'], 1)), 0),
            index=df['close'].index, columns=df['close'].columns)
        factor = ts_sum(factor, 12)
        factor = ts_rank_bk(factor, 20)
        factor = ts_mean(factor, 100)

        return factor