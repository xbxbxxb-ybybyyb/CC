from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk



class wyc_ts50_future(FactorGenerator):
    def __init__(self):

        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts50_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        returns = df['close'].pct_change(fill_method=None)
        N = 20
        factor = ts_sum((returns>0),N)
        factor = ts_mean(factor, N)
        factor = ts_rank_bk(factor, 5 * 242)
        return factor