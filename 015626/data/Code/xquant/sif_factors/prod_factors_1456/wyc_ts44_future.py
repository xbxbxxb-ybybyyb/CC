from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts44_future(FactorGenerator):
    def __init__(self):

        required_columns=['volume','close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts44_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        mask = df['recent_month_mask']
        temp1 = df['volume'].copy(deep = True)
        con1 = df['close']>delay(df['close'],1)
        con2 = df['close']<delay(df['close'],1)
        temp1[con2] = -1 * df['volume']
        factor = ts_sum(temp1,20)
        factor = mean(factor, 20)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()


        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<0]=0
        return factor
