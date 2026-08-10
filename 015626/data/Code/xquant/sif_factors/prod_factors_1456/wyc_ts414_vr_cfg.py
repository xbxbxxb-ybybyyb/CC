from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts414_vr_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['close_zz500','stk_volatility_zz500']
        lookback_bars=2000
        super(wyc_ts414_vr_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        factor = pd.DataFrame(np.where(df['close' + suffix] > delay(df['close' + suffix], 2), std(df['close' + suffix], 50), 0),
                              index=df['close' + suffix].index, columns=df['close' + suffix].columns)

        factor = ts_mean(factor, 30)

        factor = factor * (2 * df['stk_volatility_zz500'].rank(axis=1, pct=True) - 1)
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 60)
        factor = ts_mean(factor, 10)

        factor.columns = [columnname]
        factor[columnname] = rolling_normalize(factor, 5 * 242)

        # factor[factor > 0] = 0

        return factor