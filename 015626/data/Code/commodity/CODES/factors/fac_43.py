import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *


# ulb_zscore_ma
class fac_43(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'close']

        super(fac_43, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):
        ##### def data #####
        close = data['close']
        high = data['high']
        low = data['low']

        ##### calc factor #####
        def calc_ulb_zscore(close, high, low, roll_win=20, min_pct=0.9):
            upper = SMA(high, roll_win, 1)
            lower = SMA(low, roll_win, 1)
            ulb = upper - lower
            ulb_avg = ulb.rolling(roll_win, int(roll_win * min_pct)).mean()
            ulb_std = ulb.rolling(roll_win, int(roll_win * min_pct)).std()
            mid = (upper + lower) / 2
            ulb_zscore = ((close - mid) - ulb_avg) / ulb_std
            return ulb_zscore

        """ulb_zscore_ma"""
        factor_name = 'ulb_zscore_ma'
        roll_win = aaa
        ma_win = bbb
        ts_pct_win = ccc * 300
        score_raw = calc_ulb_zscore(close, high, low, roll_win)
        score_raw = score_raw.rolling(ma_win, min_periods = 1).mean()
        
        ulb_zscore_ma = ts_rank(score_raw, ts_pct_win)


        ##### format factor #####
        ulb_zscore_ma.name = self.__class__.__name__
        factor = pd.DataFrame(ulb_zscore_ma)
        return factor
