from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk


class wyc_ts19_future_nr_tr(FactorGeneratorComplex):

    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'low' + suffix,'high' + suffix,'volume' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts19_future_nr_tr, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self,df):
        columnname = self.__class__.__name__
        suffix = '_zz500'
        a = (df['high' + suffix]-df['low' + suffix])
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(((df['close' + suffix]-df['low' + suffix])-(df['high' + suffix]-df['close' + suffix]))/a*df['volume' + suffix],10)
        factor = ts_mean(factor, 30)

        factor = rolling_normalize(factor, 5 * 242)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        tr = (2 * t.rank(axis=1, pct=True) - 1)
        factor = factor * tr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 200)
        factor = ts_mean(factor, 5)
        factor = rolling_normalize(factor, 5 * 242)
        factor.columns = [columnname]

        return factor