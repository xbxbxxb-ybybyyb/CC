from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts5_future(FactorGenerator):
    def __init__(self):
        required_columns=['volume','high','close']
        lookback_bars=2000
        super(wyc_ts5_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 45
        factor = pd.DataFrame(np.where((delta((ts_sum(df['close'], N) / N), N) / delay(df['close'], N))<=0.05,(-1 * (df['close'] - ts_min(df['close'], N))),(-1 * delta(df['close'], 3))),index=df['close'].to_frame().index,columns=df['close'].to_frame().columns)
        factor = mean(ts_rank(-1*factor, 1200),15)

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
        factor[factor<=-0.5] = np.nan
        return factor