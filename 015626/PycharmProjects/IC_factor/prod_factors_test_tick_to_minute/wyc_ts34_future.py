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

class wyc_ts34_future(FactorGenerator):
    def __init__(self):

        required_columns=['close','high','low','volume']
        lookback_bars=2000
        super(wyc_ts34_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        factor = ((df.close-df.low)-(df.high-df.close))/(df.high-df.low)*df.volume
        factor = mean(factor, 150)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = ts_rank(factor, 5 * 242)
        factor[factor<-0.8]=np.nan
        return factor