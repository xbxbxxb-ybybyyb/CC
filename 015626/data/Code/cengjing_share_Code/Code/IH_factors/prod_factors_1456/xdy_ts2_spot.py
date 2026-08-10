from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts2_spot(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot', 'low_spot']
        lookback_bars=2000
        super(xdy_ts2_spot, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot']
        low = df['low_spot']
        high[abs(high) < 1e-8] = np.nan
        gain_high_20 = high / high.shift(20) - 1
        factor = (low * gain_high_20).to_frame()
        factor = ts_truncated_ema(factor, 100, 1/26).to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor[factor <= -0.3] = 0

        return factor