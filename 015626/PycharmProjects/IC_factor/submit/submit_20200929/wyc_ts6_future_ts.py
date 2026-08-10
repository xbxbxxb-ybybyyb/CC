from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts6_future_ts(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['volume' + suffix,'high' + suffix,'low' + suffix,'close' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts6_future_ts, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        N = 45
        a = (df['high' + suffix] - df['low' + suffix])
        a[abs(a) < 1e-8] = np.nan
        factor = sma(df['volume'+ suffix] * ((df['close' + suffix] - df['low' + suffix]) - (df['high' + suffix] - df['close' + suffix])) / a, N, 1)
        factor = ts_rank_bk(factor, 1200)
        factor = ts_mean(factor, 15)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        factor = factor * t
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 200)
        factor = ts_mean(factor, 10)
        factor = rolling_normalize(factor, 5 * 242)
        factor.columns = [columnname]

        return factor