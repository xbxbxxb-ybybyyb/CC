from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts44_spot(FactorGenerator):
    def __init__(self):

        required_columns=['volume_spot','close_spot']
        lookback_bars=2000
        super(wyc_ts44_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        temp1 = df['volume_spot'].copy(deep = True)
        con1 = df['close_spot']>delay(df['close_spot'],1)
        con2 = df['close_spot']<delay(df['close_spot'],1)
        temp1[con2] = -1 * df['volume_spot']
        factor = ts_sum(temp1,10)
        factor = ts_mean(factor, 10)
        factor = ts_rank(factor, 237)

        factor[factor < 0] = 0

        columnname = self.__class__.__name__
        factor.columns = [columnname]        
        return factor
