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

class zlmacd_std_zsj(FactorGenerator):
    def __init__(self):
        super(zlmacd_std_zsj, self).__init__(factor_name = 'zlmacd_std_zsj',
                                              required_columns = ['close','high','low','volume'],
                                              lookback_bars = 1400)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']
        high = data['high']
        low = data['low']

        ##### calc factor #####
        def calc_zlmacd(close, short_win=20, long_win=100):
            p1 = (2 * EMA(close, short_win) - EMA(EMA(close, short_win), short_win))
            p2 = -(2 * EMA(close, long_win) - EMA(EMA(close, long_win), long_win))
            zlmacd = p1 + p2
            return zlmacd

        """zlmacd_std"""
        factor_name = 'zlmacd_std'
        short_win = 5
        long_win = 100
        std_win = 60
        ts_pct_win = 1200
        score = calc_zlmacd(close, short_win, long_win)
        zlmacd_std = calc_std_helper(score, std_win, ts_pct_win)

        ##### format factor #####
        zlmacd_std.name = self.__class__.__name__
        factor = pd.DataFrame(zlmacd_std)
        return factor
