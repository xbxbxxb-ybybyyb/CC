from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk



class wyc_ts14_future(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts14_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        factor = pd.DataFrame(np.where(df['close'] > delay(df['close'], 2), std(df['close'], 50), 0),
                              index=df['close'].index, columns=df['close'].columns)
        factor = mean(factor, 15)
        factor = factor.fillna(method='ffill')
        factor= ts_rank(factor, 2*237)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()
                
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor