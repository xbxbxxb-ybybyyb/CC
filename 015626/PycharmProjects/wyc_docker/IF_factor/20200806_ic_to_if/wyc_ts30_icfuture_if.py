from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts30_icfuture_if(FactorGenerator):
    def __init__(self):

        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts30_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        m = 100
        p1 = 10
        p2 = 20
        RC = df.close / delay(df.close, 1)
        ARC1 = sma(delay(RC, 1), m, 1)
        DIF = ts_mean(delay(ARC1, 1), p1) - ts_mean(delay(ARC1, 1), p2)
        RCCD = sma(DIF, m, 1)
        factor = RCCD

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)

        return factor
