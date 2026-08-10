from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np

class wyc_ts34_icfuture_if(FactorGenerator):
    def __init__(self):

        required_columns=['close','high','low','volume']
        lookback_bars=2000
        super(wyc_ts34_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = ((df.close - df.low) - (df.high - df.close)) / (df.high - df.low) * df.volume
        factor = ts_mean(factor, 150)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor[factor <= -0.5] = np.nan

        return factor