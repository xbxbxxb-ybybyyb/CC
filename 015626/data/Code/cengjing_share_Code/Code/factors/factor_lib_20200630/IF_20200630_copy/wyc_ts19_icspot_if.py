from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts19_icspot_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot','low_spot','high_spot','volume_spot']
        lookback_bars=2000
        super(wyc_ts19_icspot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        a = (df['high_spot'] - df['low_spot'])
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(((df['close_spot'] - df['low_spot']) - (df['high_spot'] - df['close_spot'])) / a * df['volume_spot'], 10)

        factor = ts_rank_bk(factor, 242)
        factor = ts_mean(factor, 120)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor