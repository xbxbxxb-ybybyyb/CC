from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts5_future(FactorGenerator):
    def __init__(self):
        required_columns=['volume','high','close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts5_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        mask = df['recent_month_mask']
        N = 45
        factor = pd.DataFrame(np.where((delta((ts_sum(df['close'], N) / N), N) / delay(df['close'], N))<=0.05,(-1 * (df['close'] - ts_min(df['close'], N))),(-1 * delta(df['close'], 3))),index=df['close'].index,columns=df['close'].columns)
        # factor = mean(ts_rank(-1*factor, 600),15)

        factor = factor.fillna(method='ffill')
        factor = -1 * ts_rank(factor, 3 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor[factor<=-0.5] = 0

        return factor