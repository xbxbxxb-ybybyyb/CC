# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from utils_zsj import *

"""
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
from ts.factor.minute.utils_zsj import *
"""
class ulb_zscore_std_zsj(FactorGenerator):
    def __init__(self):
        super(ulb_zscore_std_zsj, self).__init__(factor_name = 'ulb_zscore_std_zsj',
                                              required_columns = ['close','high','low','volume'],
                                              lookback_bars = 1400)

    def on_bar(self, data):
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
        factor_name = 'ulb_zscore_std'
        std_win = 60
        roll_win = 30
        ts_pct_win = 240
        score_raw = calc_ulb_zscore(close, high, low, roll_win)
        ulb_zscore_std = calc_std_helper(score_raw, std_win, ts_pct_win)


        ##### format factor #####
        ulb_zscore_std.name = self.__class__.__name__
        factor = pd.DataFrame(ulb_zscore_std)
        factor[factor>=0.5] = np.nan
        return factor


