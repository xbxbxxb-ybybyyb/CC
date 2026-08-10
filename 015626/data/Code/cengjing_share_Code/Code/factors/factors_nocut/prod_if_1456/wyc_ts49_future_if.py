from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np


class wyc_ts49_future_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_if', 'recent_month_mask']
        lookback_bars = 2000
        super(wyc_ts49_future_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        con1 = ((delta((ts_sum(df['close_if'], 100) / 100), 100) / delay(df['close_if'], 100)) <= 0.05)
        temp1 = df['close_if'].copy(deep=True)
        temp1[con1] = (df['close_if'] - ts_min(df['close_if'], 200))
        temp1[~con1] = delta(df['close_if'], 10)
        factor = temp1
        factor = ts_rank(factor, 75)
        factor = mean(factor, 30)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        mask = df['recent_month_mask']
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
