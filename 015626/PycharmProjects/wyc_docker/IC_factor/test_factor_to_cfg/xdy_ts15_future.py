from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts15_future(FactorGenerator):
    def __init__(self):
        required_columns=['high']
        lookback_bars=2000
        super(xdy_ts15_future, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high']
        a = ts_rank_bk(high.ewm(10).mean(), 80)
        factor = ts_mean(a, 50)


        return factor