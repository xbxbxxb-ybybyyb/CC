from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts24_spot(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot','high_spot','low_spot']
        lookback_bars=2000
        super(wyc_ts24_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        
        N = 20
        wmadf = mean(df['close_spot'], N)
        long = ts_max(df['high_spot'], N) - wmadf
        short = ts_min(df['low_spot'], N) - wmadf
        factor =  (long - short) / df['close_spot']
        factor = ts_rank_bk(factor, 80)
        factor = ts_mean(factor, 40)

        return factor