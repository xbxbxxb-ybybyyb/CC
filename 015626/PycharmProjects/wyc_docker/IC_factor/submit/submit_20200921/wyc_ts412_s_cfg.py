from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts412_s_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['close_zz500','weight_boolean_zz500']
        lookback_bars=2000
        super(wyc_ts412_s_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = (ts_mean(df['close_zz500'], 3) + ts_mean(df['close_zz500'], 6) + ts_mean(df['close_zz500'], 12) + ts_mean(df['close_zz500'], 24)) / 4
        factor = ts_rank(factor, 15)
        factor = ts_mean(factor, 40)

        factor = factor[df['weight_boolean_zz500']]
        factor = factor.sum(axis=1).to_frame()

        factor.columns = [columnname]
        factor[columnname] = rolling_normalize(factor, 5 * 242)

        factor[factor < 0] = 0

        return factor