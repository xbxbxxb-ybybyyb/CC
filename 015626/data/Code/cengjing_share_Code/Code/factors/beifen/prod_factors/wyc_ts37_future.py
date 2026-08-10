from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts37_future(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts37_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        factor = -1 * sma(((df['close']-mean(df['close'],20))/mean(df['close'],20) - delay((df['close'] - mean(df['close'],20))/mean(df['close'],20),6)),12,1)

        factor = ts_rank_positive(factor, 40)
        factor = mean(factor, 50)

        def rolling_normalize(df, x):
            def normalize(dd):
                a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
                b = (a - 0.5) * 2
                return b

            return df.rolling(x, min_periods=int(x / 2)).apply(normalize)

        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor