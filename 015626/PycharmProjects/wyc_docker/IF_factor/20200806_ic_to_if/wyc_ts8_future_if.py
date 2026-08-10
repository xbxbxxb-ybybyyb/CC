from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts8_future_if(FactorGenerator):
    def __init__(self):
        required_columns=['close_if']
        lookback_bars=2000
        super(wyc_ts8_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = pd.DataFrame(
            np.where(df['close_if'] - delay(df['close_if'], 1) < 0, abs(df['close_if'] - delay(df['close_if'], 1)), 0),
            index=df['close_if'].to_frame().index, columns=df['close_if'].to_frame().columns)
        # factor = ts_mean(factor, 3)
        factor = ts_rank_bk(-1 * factor, 120)
        factor = ts_mean(factor, 240)
        factor = ts_mean(factor, 2)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor