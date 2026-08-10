import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from help_functions_wsc import multi_processing_joblib
from operators_wsc import *



class wsc8_future_if(FactorGenerator):
    def __init__(self):
        super(wsc8_future_if, self).__init__(required_columns=['close_if', 'high_if', 'low_if', 'recent_month_mask'],
                                              lookback_bars=2000)

    def on_bar(self, data):
        mask = data['recent_month_mask']
        close = data['close_if']
        high = data['high_if']
        low = data['low_if']
        n = 30
        m = 80
        low_n = ts_min(low, n)
        high_n = ts_max(high, n)
        a = high_n - low_n
        a[abs(a)<1e-8] = np.nan
        b = (close- low_n) / (high_n - low_n)
        b_low = ts_min(b, m)
        b_high = ts_max(b, m)
        c = b_high - b_low
        c[abs(c)<1e-8] = np.nan
        d = (b - b_low) / c
        e = multi_processing_joblib(d, ts_truncated_ema, n_jobs=-1, d=60, alpha=2/3)
        factor = multi_processing_joblib(e, ts_truncated_ema, n_jobs=-1, d=60, alpha=2/3)
        factor = ts_mean(factor, 140)
        factor = ts_rank(factor, 1800)
        factor = factor[mask].sum(axis=1)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        #factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
