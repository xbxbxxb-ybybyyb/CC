from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts4_icspot_if(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts4_icspot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 100
        factor = pd.DataFrame(np.where((delta((ts_sum(df['close_spot'], N) / N), N) / delay(df['close_spot'], N))<=0.05,(-1 * (df['close_spot'] - ts_min(df['close_spot'], N))),(-1 * delta(df['close_spot'], 3))),index=df['close_spot'].to_frame().index,columns=df['close_spot'].to_frame().columns)
        factor = ts_mean(ts_rank_bk(-1*factor, 100),N)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor