from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts26_future_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_if', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts26_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        N = 6
        N1 = 4
        N2 = 8
        MTM = df['close_if'] - delay(df['close_if'], 1)
        MTMMA = multi_processing_joblib(df=MTM, func=ts_truncated_ema, n_jobs=-1, d=1200, alpha= 1/N)
        DIF = ts_mean(delay(MTMMA, 1), N1) - ts_mean(delay(MTMMA, 1), N2)
        factor = multi_processing_joblib(df=DIF, func=ts_truncated_ema, n_jobs=-1, d=1200, alpha= 1/90)
        factor = ts_rank(factor, 2 * 242)
        factor = ts_mean(factor, 120)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        return factor