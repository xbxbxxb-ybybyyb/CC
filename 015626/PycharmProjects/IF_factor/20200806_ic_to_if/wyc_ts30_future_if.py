from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts30_future_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_if']
        lookback_bars=2000
        super(wyc_ts30_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        m = 100
        p1 = 10
        p2 = 20
        RC = df.close_if / delay(df.close_if, 1)
        ARC1 = sma(delay(RC, 1), m, 1)
        DIF = ts_mean(delay(ARC1, 1), p1) - ts_mean(delay(ARC1, 1), p2)
        RCCD = sma(DIF, m, 1)
        factor = RCCD
        factor = ts_rank_bk(factor, 2 * 242)
        factor = ts_mean(factor, 10)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor >= 0.5] = np.nan

        return factor
