from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts41_future_nr_vs(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'stk_volatility' + suffix]
        lookback_bars=2000
        super(wyc_ts41_future_nr_vs, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'

        columnname = self.__class__.__name__

        factor = wma(((df['close' + suffix] - delay(df['close' + suffix],3))/delay(df['close' + suffix],3)*100+(df['close' + suffix] - delay(df['close' + suffix],6))/delay(df['close' + suffix],6)*100),12)
        factor = ts_rank_bk(-1 * factor, 20)
        factor = ts_mean(factor, 20)

        factor = rolling_normalize(factor, 5 * 242)

        factor = factor * df['stk_volatility' + suffix]
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        return factor