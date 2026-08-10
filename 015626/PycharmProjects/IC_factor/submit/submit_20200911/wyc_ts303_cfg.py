from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts303_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['close_zz500','weight_zz500']
        lookback_bars=2000
        super(wyc_ts303_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        raw1 = -1 * (df['close_zz500']-ts_mean(df['close_zz500'],24))/ts_mean(df['close_zz500'],24)*100
        factor = (raw1 * df['weight_zz500']).mean(axis=1)
        factor = ts_mean(factor, 20)
        factor = -1 * rolling_normalize(factor, 5 * 242)
        factor.columns = [columnname]
        factor[factor <= -0.2] = np.nan

        return factor