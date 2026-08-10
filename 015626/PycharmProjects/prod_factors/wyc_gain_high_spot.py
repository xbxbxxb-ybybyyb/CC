from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class wyc_gain_high_spot(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot', 'close_spot']
        lookback_bars=2000
        super(wyc_gain_high_spot, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot']
        close = df['close_spot']
        N = 30
        gain_high_60 = high / high.shift(N) - 1
        h_c = close / high - 1
        factor = ts_sum(gain_high_60 / mean(h_c, N), N)
        factor = mean(factor, N) * -1
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor.loc[factor[columnname] <= -0.5] = np.nan

        return factor