from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts39_icfuture_if(FactorGenerator):
    def __init__(self):

        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts39_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = multi_processing_joblib(df=df['close'] - delay(df['close'], 20), func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/30)

        factor = ts_mean(factor, 10)
        mask = df['recent_month_mask']
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor[factor <= -0.5] = 0

        return factor