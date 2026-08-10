from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np


class xdy_ts13_spot_if(FactorGenerator):
    def __init__(self):
        required_columns = ['high_spot_if']
        lookback_bars = 2000
        super(xdy_ts13_spot_if, self).__init__(required_columns=required_columns,
                                               lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot_if']
        factor = ts_max(delta(rolling_normalize(ts_max(high, 121), 4 * 242), 15), 25)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor.loc[factor[columnname] <= -0.5] = 0

        return factor
