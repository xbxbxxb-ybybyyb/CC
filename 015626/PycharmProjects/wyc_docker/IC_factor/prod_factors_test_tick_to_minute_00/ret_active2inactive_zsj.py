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

class ret_active2inactive_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(ret_active2inactive_zsj, self).__init__(factor_name = 'ret_active2inactive_zsj',
                                              required_columns = ['close_zz500','amount_zz500'],
                                              lookback_bars = 2400)

    def on_bar(self, data):
        ##### def data #####
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500']
        stk_ret = stk_close / stk_close.shift(1) - 1
        factor_name = 'ret_active'
        ma_win = 180
        ts_pct_win = 1200
        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0
        ret_active_raw = stk_ret[active_mask].mean(axis=1)
        ret_inactive_raw = stk_ret[inactive_mask].mean(axis=1)
        ret_active2inactive_raw = ret_active_raw - ret_inactive_raw
        ret_active2inactive = calc_ma_helper(ret_active2inactive_raw, ma_win, ts_pct_win)
        ##### format factor #####
        factor = pd.DataFrame(ret_active2inactive,columns=[self.__class__.__name__])
        return factor


