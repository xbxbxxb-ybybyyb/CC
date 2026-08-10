from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts44_future(FactorGenerator):
    def __init__(self):

        required_columns=['volume','close']
        lookback_bars=2000
        super(wyc_ts44_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        
        temp1 = df['volume'].copy(deep = True)
        con2 = df['close']<delay(df['close'],1)
        temp1[con2] = -1 * df['volume']
        factor = ts_sum(temp1,20)
        factor = ts_mean(factor, 20)
        return factor
