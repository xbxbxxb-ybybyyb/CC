from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts204_future(FactorGenerator):
    def __init__(self):
        required_columns = ['close_ih']
        lookback_bars = 2000
        super(wyc_ts204_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        N = 60
        factor = pd.DataFrame(np.where((delta((ts_sum(df['close_ih'], N) / N), N) / delay(df['close_ih'], N)) <= 0.05,
                                       (-1 * (df['close_ih'] - ts_min(df['close_ih'], N))),
                                       (-1 * delta(df['close_ih'], 3))), index=df['close_ih'].to_frame().index,
                              columns=df['close_ih'].to_frame().columns)
        factor = ts_mean(ts_rank(factor, 40), 30)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor.loc[factor[columnname] >= 0.5, columnname] = np.nan
        return factor