# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from utils_zsj import *

class stk_ret_jump_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk_ret_jump_zsj, self).__init__(factor_name = 'stk_ret_jump_zsj',
                                               required_columns = ['close_zz500'],
                                               lookback_bars = 1600)

    def on_bar(self, data):
        ##### def data #####
        stk_close = data['close_zz500']
        stk_ret = stk_close / stk_close.shift(1) - 1
        factor_name = 'stk_ret_jump_zsj'
        ma_win = 180
        ts_pct_win = 1200
        stk_ret_jump_raw = (stk_ret - stk_ret.rolling(ts_pct_win, int(ts_pct_win * 0.5)).mean()).mean(axis=1)
        stk_ret_jump = calc_ma_helper(stk_ret_jump_raw, ma_win, ts_pct_win)
        ##### format factor #####
        factor = pd.DataFrame(stk_ret_jump,columns=[self.__class__.__name__])
        return factor


