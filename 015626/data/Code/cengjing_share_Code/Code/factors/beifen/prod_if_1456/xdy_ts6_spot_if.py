from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np


class xdy_ts6_spot_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_spot_if']
        lookback_bars = 2000
        super(xdy_ts6_spot_if, self).__init__(required_columns=required_columns,
                                              lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        close = df['close_spot_if']
        gain_close_30 = ts_gain(close, 15)
        factor = ts_levelchange(gain_close_30, 20)
        factor = mean(factor, 150)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        # factor.loc[factor[columnname] <= -0.3] = np.nan

        return factor
