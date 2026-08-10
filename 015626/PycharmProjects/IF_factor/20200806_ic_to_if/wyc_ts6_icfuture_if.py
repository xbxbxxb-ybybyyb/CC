from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts6_icfuture_if(FactorGenerator):
    def __init__(self):
        required_columns=['volume','high','low','close']
        lookback_bars=2000
        super(wyc_ts6_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

        
    def on_bar(self, df):
        columnname = self.__class__.__name__

        N = 45
        factor = sma(df['volume'] * ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low']),
                     N, 1)
        factor = ts_rank_bk(factor.to_frame(), 1200)
        factor = mean(factor, 15)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor <= -0.5] = np.nan
        return factor