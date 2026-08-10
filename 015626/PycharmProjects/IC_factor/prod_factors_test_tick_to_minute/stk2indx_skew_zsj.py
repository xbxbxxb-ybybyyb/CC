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

class stk2indx_skew_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk2indx_skew_zsj, self).__init__(factor_name = 'stk2indx_skew_zsj',
                                              required_columns = ['close_zz500'],
                                              lookback_bars = 2400)

    def on_bar(self, data):
        ##### def data #####
        stk_close = data['close_zz500']
        stk_ret = stk_close / stk_close.shift(1) - 1
        factor_name = 'stk2indx_skew_zsj'
        ma_win = 20
        ts_pct_win = 1200
        stk2indx_skew_raw = stk_ret.skew(axis=1).rolling(5,min_periods=2).mean()
        stk2indx_skew = calc_ma_helper(stk2indx_skew_raw, ma_win, ts_pct_win)
        ##### format factor #####
        factor = pd.DataFrame(stk2indx_skew,columns=[self.__class__.__name__])
        return factor


