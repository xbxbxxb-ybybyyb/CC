from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts301_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['close_zz500','low_zz500','high_zz500']
        lookback_bars=2000
        super(wyc_ts301_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        temp = df['close_zz500'].copy(deep=True)
        con1 = df['close_zz500'] == delay(df['close_zz500'], 1)
        temp[con1] = 0
        con2 = df['close_zz500'] > delay(df['close_zz500'], 1)
        temp[~con1 & con2] = df['close_zz500'] - MIN(df['low_zz500'], delay(df['close_zz500'], 1))
        temp[~con1 & ~con2] = df['close_zz500'] - MAX(df['high_zz500'], delay(df['close_zz500'], 1))
        temp = -1 * ts_sum(temp, 20)
        temp_mean = temp.mean(axis=1).to_frame()

        factor = temp_mean.copy()
        factor = -1 * ts_mean(factor, 20)
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor <= -0.2] = np.nan

        return factor