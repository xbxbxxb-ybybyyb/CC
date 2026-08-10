from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts6_future_if(FactorGenerator):
    def __init__(self):
        required_columns=['volume_if','high_if','low_if','close_if']
        lookback_bars=2000
        super(wyc_ts6_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        N = 30
        factor = sma(df['volume_if'] * ((df['close_if'] - df['low_if']) - (df['high_if'] - df['close_if'])) / (
                    df['high_if'] - df['low_if']), N, 1)
        factor = ts_rank_bk(factor.to_frame(), 1200)
        factor = mean(factor, 15)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor