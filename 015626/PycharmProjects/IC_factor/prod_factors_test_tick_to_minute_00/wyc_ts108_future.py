from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts108_future(FactorGenerator):
    def __init__(self):
        required_columns=['close_if']
        lookback_bars=2000
        super(wyc_ts108_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        key = 'close_if'
        factor = pd.DataFrame(np.where(df[key] - delay(df[key], 1) < 0, abs(df[key] - delay(df[key], 1)), 0),
                              index=df[key].to_frame().index, columns=df[key].to_frame().columns)
        factor = ts_sum(factor, 12)
        factor = ts_rank_bk(factor, 20)
        factor = ts_mean(factor, 80)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor <= -0.5] = np.nan
        return factor