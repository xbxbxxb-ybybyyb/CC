from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np


class wyc_ts2_future_if(FactorGenerator):
    def __init__(self):
        required_columns=['close_if', 'volume_if']
        lookback_bars=2000
        super(wyc_ts2_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        factor = ts_mean(ts_mean((sign(delta(df['volume_if'], 5)) * (-1 * delta(df['close_if'], 5))), 10), 20)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor < -0.5] = np.nan

        return factor