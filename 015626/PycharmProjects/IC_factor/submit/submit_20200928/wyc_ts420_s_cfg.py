from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts420_s_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['close_zz500','high_zz500','low_zz500','volume_zz500','weight_boolean_zz500']
        lookback_bars=2000
        super(wyc_ts420_s_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        factor = ts_sum(((df['close'+suffix]-df['low'+suffix])-(df['high'+suffix]-df['close'+suffix]))/(df['high'+suffix]-df['low'+suffix])*df['volume'+suffix], 20)
        factor = ts_mean(factor, 5)
        factor = ts_rank(factor, 4*242)
        finaldf = ts_mean(factor, 20)

        factor = finaldf[df['weight_boolean_zz500']]
        factor = factor.sum(axis=1).to_frame()

        factor.columns = [columnname]
        factor[columnname] = rolling_normalize(factor, 5 * 242)

        factor[factor < 0] = 0

        return factor