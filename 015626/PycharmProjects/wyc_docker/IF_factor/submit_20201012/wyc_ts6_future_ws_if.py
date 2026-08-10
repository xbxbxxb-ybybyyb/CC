from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts6_future_ws_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['volume' + suffix,'high' + suffix,'low' + suffix,'close' + suffix,'weight' + suffix]
        lookback_bars=2000
        super(wyc_ts6_future_ws_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        N = 45
        a = (df['high' + suffix] - df['low' + suffix])
        a[abs(a) < 1e-8] = np.nan
        factor = sma(df['volume'+ suffix] * ((df['close' + suffix] - df['low' + suffix]) - (df['high' + suffix] - df['close' + suffix])) / a, N, 1)
        factor = ts_rank_bk(factor, 1200)
        factor = ts_mean(factor, 15)

        factor = factor * df['weight' + suffix]
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 150)
        factor = ts_mean(factor, 10)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]
        factor[factor > 0] = 0

        return factor