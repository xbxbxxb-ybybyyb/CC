from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts1_spot(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot', 'close_spot']
        lookback_bars=2000
        super(xdy_ts1_spot, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot']
        close = df['close_spot']
        gain_high_60 = high / high.shift(60) - 1
        h_c = close / high - 1
        factor = ts_sum(gain_high_60 / mean(h_c, 60), 10)
        factor = mean(factor, 10) * -1
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor.loc[factor[columnname] <= -0.5] = np.nan

        return factor