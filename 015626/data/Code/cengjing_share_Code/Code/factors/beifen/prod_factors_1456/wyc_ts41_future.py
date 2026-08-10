from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts41_future(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts41_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        factor = wma(((df['close'] - delay(df['close'],3))/delay(df['close'],3)*100+(df['close'] - delay(df['close'],6))/delay(df['close'],6)*100),12)
        factor = ts_rank_positive(-1 * factor, 20)
        factor = mean(factor, 20)
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor