from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts37_icspot_if(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts37_icspot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = -1 * sma(((df.close_spot - mean(df.close_spot, 25)) / mean(df.close_spot, 25) - delay(
            (df.close_spot - mean(df.close_spot, 25)) / mean(df.close_spot, 25), 6)), 12, 5)

        factor = ts_rank_bk(factor, 25)
        factor = ts_mean(factor, 50)

        # factor.iloc[:, 0] = factor.iloc[:, 0].rolling(5, min_periods = 2).mean()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor >= 0.5] = np.nan
        
        return factor