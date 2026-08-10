from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts419_cs_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['close_zz500','high_zz500','low_zz500','volume_zz500','stk_index_corr_zz500']
        lookback_bars=2000
        super(wyc_ts419_cs_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        factor = ts_sum(((df['close' + suffix] - df['low' + suffix]) - (df['high' + suffix] - df['close' + suffix])) / (
                    df['high' + suffix] - df['low' + suffix]) * df['volume' + suffix], 10)
        finaldf = ts_mean(factor, 30)

        factor = finaldf * df['stk_index_corr_zz500']
        factor = factor.sum(axis=1).to_frame()
        factor.columns = [columnname]
        factor[columnname] = rolling_normalize(factor, 5 * 242)

        return factor