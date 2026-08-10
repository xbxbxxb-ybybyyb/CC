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

class pos_ma_long_zsj(FactorGenerator):
    def __init__(self):
        super(pos_ma_long_zsj, self).__init__(factor_name = 'pos_ma_long_zsj',
                                              required_columns = ['close','high','low','volume'],
                                              lookback_bars = 1400)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']

        ##### calc factor #####
        def calc_pos(close, roll_win=100):
            price = (close - REF(close, roll_win)) / REF(close, roll_win)
            pos = (price - MIN(price, roll_win)) / (MAX(price, roll_win) - MIN(price, roll_win))
            return pos

        """pos_ma_long"""
        factor_name = 'pos_ma_long'
        roll_win = 120
        ma_win = 15
        ts_pct_win = 1200
        score_raw = calc_pos(close, roll_win)
        pos_ma_long = calc_ma_helper(score_raw, ma_win, ts_pct_win)

        ##### format factor #####
        pos_ma_long.name = self.__class__.__name__
        factor = pd.DataFrame(pos_ma_long)  
        #factor[factor>=0.5] = np.nan
        return factor