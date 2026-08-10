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

class kpz_ma_displaced_std_zsj_if(FactorGenerator):
    def __init__(self):
        super(kpz_ma_displaced_std_zsj_if, self).__init__(required_columns = ['close', 'recent_month_mask'],
                                                   lookback_bars = 1500)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']
        mask = data['recent_month_mask']

        ##### calc factor #####

        def calc_ma_displaced(close, short_win=10, long_win=20):
            ma_close = MA(close, long_win)
            ma_displaced = REF(ma_close, short_win)
            ma_diff = close - ma_displaced
            return ma_diff

        factor_name = 'ma_displaced_std'
        short_win = 10
        long_win = 90
        std_win = 40
        ts_pct_win = 242*5
        score_raw = calc_ma_displaced(close, short_win, long_win)
        ma_displaced_std = calc_std_helper(score_raw, std_win, ts_pct_win)
        ma_displaced_std = ma_displaced_std[mask].sum(axis=1)

        ##### format factor #####
        ma_displaced_std.name = self.__class__.__name__
        factor = pd.DataFrame(ma_displaced_std) 
        return factor
