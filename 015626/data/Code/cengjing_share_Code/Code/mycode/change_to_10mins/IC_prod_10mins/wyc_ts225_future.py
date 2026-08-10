from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts225_future(FactorGenerator):
    def __init__(self):

        required_columns=['close_ih', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts225_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        columnname = self.__class__.__name__
        cih = df['close_ih']
        cih[abs(cih) < 1e-8] = np.nan
        factor = mean(cih, 20) / cih
        factor = ts_rank(factor, 20)
        factor = ts_mean(factor, 60)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 237)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()
        factor[factor > 0] = 0        
        factor.columns = [columnname]

        return factor