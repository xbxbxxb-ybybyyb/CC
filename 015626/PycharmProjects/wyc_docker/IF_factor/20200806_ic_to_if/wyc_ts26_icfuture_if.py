from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts26_icfuture_if(FactorGenerator):
    def __init__(self):

        required_columns=['close']
        lookback_bars=2000
        super(wyc_ts26_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        N = 6
        N1 = 4
        N2 = 8
        MTM = df.close - delay(df.close, 1);
        MTMMA = sma(MTM, N, 1);
        DIF = ts_mean(delay(MTMMA, 1), N1) - ts_mean(delay(MTMMA, 1), N2)
        factor = sma(DIF, 60, 1)
        factor = ts_rank_bk(factor, 5 * 242)
        factor = ts_mean(factor, 242)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor <= 0] = np.nan
        return factor