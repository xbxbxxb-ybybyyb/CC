from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts14_spot(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts14_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, df):
        factor = pd.DataFrame(np.where(df['close_spot'] > delay(df['close_spot'], 1), std(df['close_spot'], 50), 0),
                              index=df['close_spot'].to_frame().index, columns=df['close_spot'].to_frame().columns)
        factor = ts_rank_positive(factor, 120)
        factor = mean(factor, 20)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = self.ts_rank(factor, 5 * 242)
        factor.iloc[:, 0] =  factor.iloc[:, 0].rolling(3, min_periods = 2).mean()
        return factor