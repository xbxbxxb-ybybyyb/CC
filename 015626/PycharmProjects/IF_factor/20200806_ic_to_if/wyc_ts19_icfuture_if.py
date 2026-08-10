from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk


class wyc_ts19_icfuture_if(FactorGenerator):
    def __init__(self):

        required_columns=['close','low','high','volume']
        lookback_bars=2000
        super(wyc_ts19_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self,df):
        columnname = self.__class__.__name__

        factor = ts_sum(((df.close - df.low) - (df.high - df.close)) / (df.high - df.low) * df.volume, 20)
        # factor = ts_rank(factor, 60)
        factor = ts_mean(factor, 30)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 1200)

        return factor