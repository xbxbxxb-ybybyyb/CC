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
class vma_std_zsj(FactorGenerator):
    def __init__(self):
        super(vma_std_zsj, self).__init__(factor_name = 'vma_std_zsj',
                                              required_columns = ['close','high','low','open'],
                                              lookback_bars = 1400)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']
        high = data['high']
        low = data['low']
        ts_open = data['open']

        def calc_vma(high, low, ts_open, close, roll_win=20):
            price = (high + low + ts_open + close) / 4
            vma = MA(price, roll_win)
            vma_diff = close - vma
            return vma_diff

        factor_name = 'vma_std'
        roll_win = 30
        std_win = 20
        ts_pct_win = 240*5
        score = calc_vma(high, low, ts_open, close, roll_win)
        vma_std = calc_ma_helper(score, std_win, ts_pct_win)
        
        ##### format factor #####
        vma_std.name = self.__class__.__name__
        factor = pd.DataFrame(vma_std)
        factor[factor<0]=np.nan
        return factor
