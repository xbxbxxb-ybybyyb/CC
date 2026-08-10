from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts2_future(FactorGenerator):
    def __init__(self):
        required_columns=['high', 'low']
        lookback_bars=2000
        super(xdy_ts2_future, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high']
        low = df['low']
        gain_high_20 = high / high.shift(20) - 1
        factor = (low * gain_high_20).to_frame().ewm(40).mean()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor[factor <= -0.3] = np.nan

        return factor