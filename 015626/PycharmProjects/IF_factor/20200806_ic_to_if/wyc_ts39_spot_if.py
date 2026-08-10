from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts39_spot_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot_if']
        lookback_bars=2000
        super(wyc_ts39_spot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = sma(df.close_spot_if - delay(df.close_spot_if, 20), 20, 1)
        factor = ts_mean(factor, 20)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)

        return factor