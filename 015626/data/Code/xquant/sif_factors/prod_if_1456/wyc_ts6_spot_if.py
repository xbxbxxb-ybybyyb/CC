from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts6_spot_if(FactorGenerator):
    def __init__(self):
        required_columns=['volume_spot_if','high_spot_if','low_spot_if','close_spot_if']
        lookback_bars=2000
        super(wyc_ts6_spot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        N = 20
        a = (df['high_spot_if'] - df['low_spot_if'])
        a[abs(a) < 1e-8] = np.nan
        factor = sma(df['volume_spot_if'] * (
                    (df['close_spot_if'] - df['low_spot_if']) - (df['high_spot_if'] - df['close_spot_if'])) / a, N, 1)
        factor = ts_rank_bk(factor, 240)
        factor = ts_mean(factor, 20)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor
