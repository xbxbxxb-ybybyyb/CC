from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np


class wyc_ts47_future_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_if', 'recent_month_mask']
        lookback_bars = 2000
        super(wyc_ts47_future_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        con1 = df['close_if'] > delay(df['close_if'], 4)
        factor = con1.rolling(50).sum()
        factor = mean(factor, 20)
        mask = df['recent_month_mask']
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
