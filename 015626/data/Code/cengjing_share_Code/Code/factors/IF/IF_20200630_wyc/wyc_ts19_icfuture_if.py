from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk


class wyc_ts19_icfuture_if(FactorGenerator):
    def __init__(self):

        required_columns=['close','low','high','volume', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts19_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self,df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        a = (df['high'] - df['low'])
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(((df['close'] - df['low']) - (df['high'] - df['close'])) / a * df['volume'], 20)
        # factor = ts_rank(factor, 60)
        factor = ts_mean(factor, 30)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 1200)
        factor = factor[mask].sum(axis=1).to_frame()

        factor.columns = [columnname]

        return factor