from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts47_future_nr_tr_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['close' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts47_future_nr_tr_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        con1 = df['close' + suffix] > delay(df['close' + suffix], 1)
        factor = con1.rolling(100).sum()
        factor = ts_mean(factor, 20)

        factor = rolling_normalize(factor, 5 * 242)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        tr = (2 * t.rank(axis=1, pct=True) - 1)
        factor = factor * tr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 300)
        factor = ts_mean(factor, 10)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor < 0] = 0

        return factor