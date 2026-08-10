from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts305_stix5_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['close_zz500']
        lookback_bars=2000
        super(wyc_ts305_stix5_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        c_ret5 = df['close_zz500'] - df['close_zz500'].shift(5)
        upclose = (c_ret5 > 0).sum(axis=1)
        downclose = (c_ret5 <= 0).sum(axis=1)
        factor = upclose / (upclose + downclose)
        factor = factor.ewm(30, adjust=False).mean()
        factor = ts_mean(factor, 19)
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = ts_rank_bk(factor, 2 * 242)
        factor[factor < -0.05] = 0

        return factor