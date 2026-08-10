from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class wyc_gain_high_spot_if(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot_if', 'close_spot_if']
        lookback_bars=2000
        super(wyc_gain_high_spot_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot_if']
        close = df['close_spot_if']
        N = 30
        gain_high_60 = high / high.shift(N) - 1
        h_c = close / high - 1
        a = mean(h_c, N)
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(gain_high_60 / a, N)
        factor = mean(factor, N) * -1
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        # factor.loc[factor[columnname] <= -0.5] = 0

        return factor