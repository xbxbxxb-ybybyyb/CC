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

class t3_change_zsj(FactorGenerator):
    def __init__(self):
        super(t3_change_zsj, self).__init__(factor_name = 't3_change_zsj',
                                              required_columns = ['close','high','low','volume'],
                                              lookback_bars = 1400)

    def EMA(self, df, roll_win):
        return df.ewm(span=roll_win,adjust=False,min_periods=int(roll_win/2)).mean()
    
    def on_bar(self, data):
        ##### def data #####
        close = data['close']
        
        ##### calc factor #####
        
        def calc_t3(close, roll_win=100, va=0.8):
            t1 = self.EMA(close, roll_win) * (1 + va) - self.EMA(self.EMA(close, roll_win), roll_win) * va
            t2 = self.EMA(t1, roll_win) * (1 + va) - self.EMA(self.EMA(t1, roll_win), roll_win) * va
            t3 = self.EMA(t2, roll_win) * (1 + va) - self.EMA(self.EMA(t2, roll_win), roll_win) * va
            t3_diff = close - t3
            return t3_diff

        factor_name = 't3_change'
        short_win = 10
        long_win = 30
        ts_pct_win = 1200
        roll_win = 5
        sign = -1
        score = calc_t3(close, roll_win)
        t3_change = calc_change_helper(score, short_win, long_win, ts_pct_win, sign)
        t3_change = t3_change.rolling(3, min_periods = 2).mean()
        ##### format factor #####
        t3_change.name = self.__class__.__name__
        factor = pd.DataFrame(t3_change)
        return factor


