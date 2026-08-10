from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts13_future(FactorGenerator):
    def __init__(self):
        required_columns=['high', 'recent_month_mask']
        lookback_bars=2000
        super(xdy_ts13_future, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        high = df['high']
        factor = ts_max(delta(rolling_norm(ts_max(high,121),3*242),15),19)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        # factor.loc[factor[columnname] <= 0] = 0

        return factor