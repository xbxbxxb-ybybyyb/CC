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
        factor = mean(df['close_ih'], 20) / df['close_ih']
        factor = ts_rank_bk(factor, 20)
        factor = ts_mean(factor, 60)
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()        
        factor.columns = [columnname]

        return factor