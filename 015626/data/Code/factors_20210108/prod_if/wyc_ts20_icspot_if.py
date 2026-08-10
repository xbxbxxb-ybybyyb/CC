from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts20_icspot_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot','low_spot','high_spot','volume_spot']
        lookback_bars=2000
        super(wyc_ts20_icspot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        a = (df['high_spot'] - df['low_spot'])
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(((df['close_spot'] - df['low_spot']) - (df['high_spot'] - df['close_spot'])) / a * df['volume_spot'], 20)
        # factor = ts_mean(factor, 5)
        factor = ts_rank(factor, 4 * 242)
        factor = ts_mean(factor, 20)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 4 * 242)
        return factor