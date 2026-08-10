from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts21_spot_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot_if']
        lookback_bars=2000
        super(wyc_ts21_spot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        M = 4
        RC = df.close_spot_if / delay(df.close_spot_if, M)
        factor = sma(delay(RC, 1), M, 1)
        factor = ts_rank_bk(factor, 242 * 4)
        factor = ts_mean(factor, 30)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)

        return factor
