from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np


class wyc_ts7_future_vr_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'

        required_columns=['close' + suffix, 'stk_volatility' + suffix]
        lookback_bars=2000
        super(wyc_ts7_future_vr_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        N = 15
        logclose = log(df['close' + suffix])
        s1 = multi_processing_joblib(df=logclose, func=ts_truncated_ema, n_jobs=-1, d=60, alpha= 2/N)
        s2 = multi_processing_joblib(df=s1, func=ts_truncated_ema, n_jobs=-1, d=60, alpha= 2/N)
        s3 = multi_processing_joblib(df=s2, func=ts_truncated_ema, n_jobs=-1, d=60, alpha= 2/N)
        s3[abs(s3) < 1e-8] = np.nan
        factor = s3 / delay(s3, 1) - 1
        
        factor = ts_mean(factor, 10)

        vr = (2 * df['stk_volatility' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * vr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        return factor