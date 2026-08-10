from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np

class wyc_ts34_icfuture_if(FactorGenerator):
    def __init__(self):

        required_columns=['close','high','low','volume', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts34_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        a = (df['high'] - df['low'])
        a[abs(a) < 1e-8] = np.nan
        factor = ((df['close'] - df['low']) - (df['high'] - df['close'])) / a * df['volume']
        factor = ts_mean(factor, 150)
        mask = df['recent_month_mask']
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor[factor <= -0.5] = 0

        return factor