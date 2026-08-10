from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk
from operators_wyc import *

class wyc_ts14_spot(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts14_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        factor = pd.DataFrame(np.where(df['close_spot'] > delay(df['close_spot'], 1), std(df['close_spot'], 50), 0),
                              index=df['close_spot'].to_frame().index, columns=df['close_spot'].to_frame().columns)
        factor = ts_rank(factor, 120)
        factor = mean(factor, 20)

        factor = factor.fillna(method='ffill')
        factor = ts_rank(factor, 3 * 237)
        
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor