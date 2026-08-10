from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk



class wyc_ts29_icfuture_if(FactorGenerator):
    def __init__(self):
        lookback_bars = 2000
        required_columns = ['close', 'volume', 'recent_month_mask']
        super(wyc_ts29_icfuture_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        N = 20
        dfclose = df['close']
        dfclose[abs(dfclose) < 1e-8] = np.nan
        factor = (df['close'] - delay(df['close'], N)) / delay(dfclose, N) * df['volume']
        factor = ts_rank(factor, 300)
        factor = ts_mean(factor, 20)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1).to_frame()

        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0

        return factor
