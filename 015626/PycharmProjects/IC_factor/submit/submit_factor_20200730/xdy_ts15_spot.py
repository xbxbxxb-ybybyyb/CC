from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts15_spot(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot']
        lookback_bars=2000
        super(xdy_ts15_spot, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot']
        a = rolling_normalize(ts_rank(wma(high.to_frame(), 70), 55), 3 * 242)
        factor = mean(a, 63)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)

        return factor