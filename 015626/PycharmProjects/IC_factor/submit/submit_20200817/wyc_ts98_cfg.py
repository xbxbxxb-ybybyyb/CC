from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np

class wyc_ts98_cfg(FactorGenerator):
    def __init__(self):

        required_columns=['close_zz500']
        lookback_bars=2000
        super(wyc_ts98_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        con1 = ((delta((ts_sum(df['close_zz500'], 100) / 100), 100) / delay(df['close_zz500'], 100)) <= 0.05)
        temp = df['close_zz500'].copy(deep=True)
        temp[con1] = (-1 * (df['close_zz500'] - ts_min(df['close_zz500'], 100)))
        temp[~con1] = -1 * delta(df['close_zz500'], 3)

        factor = temp.mean(axis=1).to_frame() * -1
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 7 * 242)
        factor[factor <= -0.85] = np.nan

        return factor