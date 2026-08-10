from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts37_spot(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts37_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__


        cmcs = mean(df['close_spot'],25)
        cmcs[abs(cmcs) < 1e-6] = np.nan
        factor = (df['close_spot']-mean(df['close_spot'],25))/cmcs - delay((df['close_spot'] - mean(df['close_spot'],25))/cmcs,6)
        factor = -1 * ts_truncated_ema(factor, 100, 5/12)

        factor = ts_rank_positive(factor, 25)
        factor = mean(factor, 50)

        factor = factor.to_frame()
        factor.iloc[:, 0] = factor.iloc[:, 0].rolling(5, min_periods = 2).mean()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        
        return factor