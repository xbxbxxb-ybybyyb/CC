from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts6_spot(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']
        lookback_bars=2000
        super(xdy_ts6_spot, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        close = df['close_spot']
        gain_close_30 = ts_gain(close, 30)
        factor = ts_levelchange(gain_close_30, 20)
        factor = ts_mean(factor, 110)

        return factor