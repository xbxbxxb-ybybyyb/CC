from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts28_icfuture_if(FactorGenerator):
    def __init__(self):

        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts28_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        M = 10
        con1 = df.close > delay(df.close, M)
        factor = ts_sum(con1, M) / M * 100
        factor = ts_mean(factor, 40)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor <= -0.2] = np.nan
        return factor
