from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts13_spot(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot']
        lookback_bars=2000
        super(xdy_ts13_spot, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot']
        factor = ts_max(delta(rolling_norm(ts_max(high,121),3*242),15),19)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        factor.loc[factor[columnname] <= 0] = 0

        return factor