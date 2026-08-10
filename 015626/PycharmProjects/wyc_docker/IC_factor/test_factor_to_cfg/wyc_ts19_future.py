from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk


class wyc_ts19_future(FactorGenerator):
    def __init__(self):

        required_columns=['close','low','high','volume']
        lookback_bars=2000
        super(wyc_ts19_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self,df):
        a = (df['high']-df['low'])
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(((df['close']-df['low'])-(df['high']-df['close']))/a*df['volume'],10)
        factor = ts_mean(factor, 30)

        return factor