from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts3_future(FactorGenerator):
    def __init__(self):
        required_columns=['vwap', 'close']
        lookback_bars=2000
        super(xdy_ts3_future, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        vwap = df['vwap']
        close = df['close']
        gain_close_30 = close / close.shift(30) - 1
        factor = (vwap * gain_close_30).rolling(15, min_periods=5).median()
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor.loc[factor[columnname] <= -0.5] = np.nan

        return factor