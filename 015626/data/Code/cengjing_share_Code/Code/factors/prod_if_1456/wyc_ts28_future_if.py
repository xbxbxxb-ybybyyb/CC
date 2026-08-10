from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts28_future_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_if', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts28_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        M = 40
        con1 = df['close_if'] > delay(df['close_if'], 20)
        factor = ts_sum(con1, M) / M * 100
        factor = ts_mean(factor, 30)
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1).to_frame()

        factor.columns = [columnname]
        factor[factor <= -0.2] = 0
        return factor
