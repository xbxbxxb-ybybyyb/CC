from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts4_future_if(FactorGenerator):
    def __init__(self):
        required_columns=['close_if']
        lookback_bars=2000
        super(wyc_ts4_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        N = 240
        factor = pd.DataFrame(np.where((delta((ts_sum(df['close_if'], N) / N), N) / delay(df['close_if'], N)) <= 0.05,
                                       (-1 * (df['close_if'] - ts_min(df['close_if'], N))),
                                       (-1 * delta(df['close_if'], 3))), index=df['close_if'].to_frame().index,
                              columns=df['close_if'].to_frame().columns)
        factor = ts_mean(ts_rank_bk(-1 * factor, 80), 20)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor