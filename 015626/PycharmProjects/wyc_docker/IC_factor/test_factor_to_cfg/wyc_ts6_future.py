from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts6_future(FactorGenerator):
    def __init__(self):
        required_columns=['volume','high','low','close']
        lookback_bars=2000
        super(wyc_ts6_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

        
    def on_bar(self, df):

        
        N = 45
        a = (df['high'] - df['low'])
        a[abs(a) < 1e-8] = np.nan
        factor = sma(df['volume'] * ((df['close'] - df['low']) - (df['high'] - df['close'])) / a, N, 1)
        factor = ts_rank_bk(factor, 1200)
        factor = ts_mean(factor, 15)



        return factor