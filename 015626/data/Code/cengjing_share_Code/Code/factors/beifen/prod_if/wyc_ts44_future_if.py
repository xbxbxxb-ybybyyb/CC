from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np


class wyc_ts44_future_if(FactorGenerator):
    def __init__(self):
        required_columns = ['volume_if', 'close_if', 'recent_month_mask']
        lookback_bars = 2000
        super(wyc_ts44_future_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        temp1 = df['volume_if'].copy(deep=True)
        con1 = df['close_if'] > delay(df['close_if'], 1)
        con2 = df['close_if'] < delay(df['close_if'], 1)
        temp1[con2] = -1 * df['volume_if']
        factor = ts_sum(temp1, 15)
        factor = mean(factor, 60)
        mask = df['recent_month_mask']
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor < 0] = 0
        return factor
