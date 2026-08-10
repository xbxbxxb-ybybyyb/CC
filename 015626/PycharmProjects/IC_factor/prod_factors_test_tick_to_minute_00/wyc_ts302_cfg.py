from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts302_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['volume_zz500','high_zz500','weight_zz500']
        lookback_bars=2000
        super(wyc_ts302_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        temp = (-1 * ts_max(correlation(ts_rank_bk(df['volume_zz500'], 5), ts_rank_bk(df['high_zz500'], 5), 5), 3))
        temp_weight = temp * df['weight_zz500']
        temp_weight_mean = temp_weight.mean(axis=1).to_frame()

        factor = temp_weight_mean.copy()
        factor = -1 * ts_mean(factor, 30)
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor <= -0.3] = np.nan

        return factor