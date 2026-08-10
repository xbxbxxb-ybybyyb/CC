from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts6_future(FactorGenerator):
    def __init__(self):
        required_columns=['volume','high','low','close']
        lookback_bars=2000
        super(wyc_ts6_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
        
    def on_bar(self, df):

        
        N = 45
        factor = sma(df['volume'] * ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low']), N, 1)
        factor = self.ts_rank(factor.to_frame(), 1200)
        factor.iloc[:, 0] = mean(factor.iloc[:,0], 15)

        

        def rolling_normalize(df, x):
            def normalize(dd):
                a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
                b = (a - 0.5) * 2
                return b

            return df.rolling(x, min_periods=int(x / 2)).apply(normalize)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor<=-0.5] = 0
        return factor