from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np

class wyc_ts14_future_if(FactorGenerator):
    def __init__(self):
        required_columns=['close_if']
        lookback_bars=2000
        super(wyc_ts14_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = pd.DataFrame(np.where(df['close_if'] > delay(df['close_if'], 2), std(df['close_if'], 50), 0),
                              index=df['close_if'].to_frame().index, columns=df['close_if'].to_frame().columns)
        factor = ts_rank_bk(factor, 80)
        factor = ts_mean(factor, 40)
        # factor = ts_mean(factor, 30)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 3 * 242)
        factor[factor <= -0.5] = np.nan
        return factor