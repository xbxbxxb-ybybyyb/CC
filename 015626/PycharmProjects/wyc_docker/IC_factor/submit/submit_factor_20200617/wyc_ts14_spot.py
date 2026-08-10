from factor_generator import FactorGenerator
from operators import *
import pandas as pd
import numpy as np
class wyc_ts14_spot(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts14_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        factor = pd.DataFrame(np.where(df['close_spot'] > delay(df['close_spot'], 2), std(df['close_spot'], 50), 0),
                              index=df['close_spot'].to_frame().index, columns=df['close_spot'].to_frame().columns)
        factor = ts_rank(factor, 30)
        factor = mean(factor, 50)

        def rolling_normalize(df, x):
            def normalize(dd):
                a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
                b = (a - 0.5) * 2
                return b

            return df.rolling(x, min_periods=int(x / 2)).apply(normalize)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor