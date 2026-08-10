from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

def ts_rank(test, n=1200):
    a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
    aa = pd.DataFrame(a)
    aa.index = test.index
    aa.columns = test.columns
    return aa

class wyc_ts14_future(FactorGenerator):
    def __init__(self):
        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts14_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        factor = pd.DataFrame(np.where(df['close'] > delay(df['close'], 2), std(df['close'], 50), 0),
                              index=df['close'].to_frame().index, columns=df['close'].to_frame().columns)
        factor = mean(factor, 30)
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor= ts_rank(factor, 3 * 242)
        return factor