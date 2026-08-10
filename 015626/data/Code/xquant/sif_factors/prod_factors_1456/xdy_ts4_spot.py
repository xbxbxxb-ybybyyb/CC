from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts4_spot(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot']
        lookback_bars=2000
        super(xdy_ts4_spot, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot']
        factor = ts_position(high, 30)
        factor = -1 * factor.rolling(100, min_periods=20).skew()
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        # factor.loc[factor[columnname] <= -0.5] = 0

        return factor