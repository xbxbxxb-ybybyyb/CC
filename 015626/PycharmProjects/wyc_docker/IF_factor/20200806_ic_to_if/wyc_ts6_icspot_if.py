from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts6_icspot_if(FactorGenerator):
    def __init__(self):
        required_columns=['volume_spot','high_spot','low_spot','close_spot']
        lookback_bars=2000
        super(wyc_ts6_icspot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        N = 20
        factor = sma(
            df['volume_spot'] * ((df['close_spot'] - df['low_spot']) - (df['high_spot'] - df['close_spot'])) / (
                        df['high_spot'] - df['low_spot']), N, 1)
        factor = ts_rank_bk(factor, 80)
        factor = ts_mean(factor, 30)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor
