from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts13_future(FactorGenerator):
    def __init__(self):
        required_columns=['high']
        lookback_bars=2000
        super(xdy_ts13_future, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high']
        factor = ts_max(delta(rolling_normalize(ts_max(high,121),3*242),15),19)
    
        return factor