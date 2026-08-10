from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np


class wyc_ts44_spot_if(FactorGenerator):
    def __init__(self):
        required_columns = ['volume_spot_if', 'close_spot_if']
        lookback_bars = 2000
        super(wyc_ts44_spot_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        temp1 = df['volume_spot_if'].copy(deep=True)
        con1 = df['close_spot_if'] > delay(df['close_spot_if'], 1)
        con2 = df['close_spot_if'] < delay(df['close_spot_if'], 1)
        temp1[con2] = -1 * df['volume_spot_if']
        factor = ts_sum(temp1, 25)
        factor = mean(factor, 40)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        return factor
