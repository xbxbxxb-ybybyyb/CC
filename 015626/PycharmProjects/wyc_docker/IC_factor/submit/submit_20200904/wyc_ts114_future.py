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

class wyc_ts114_future(FactorGenerator):
    def __init__(self):
        required_columns=['close_if']
        lookback_bars=2000
        super(wyc_ts114_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        columnname = self.__class__.__name__
        key = 'close_if'
        factor = pd.DataFrame(np.where(df[key] > delay(df[key], 3), std(df[key], 30), 0),
                              index=df[key].to_frame().index, columns=df[key].to_frame().columns)
        factor = ts_mean(factor, 30)
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = ts_rank_bk(factor, 5 * 242)
        factor[factor < -0.85] = np.nan
        return factor