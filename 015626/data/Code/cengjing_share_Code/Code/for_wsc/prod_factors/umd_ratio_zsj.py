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

def rolling_normalize(sig, window = 100):
    sig_max = sig.rolling(window,min_periods=int(window/2)).max()
    sig_min = sig.rolling(window,min_periods=int(window/2)).min()
    return ((sig-sig_min)/(sig_max-sig_min))*2-1

class umd_ratio_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(umd_ratio_zsj, self).__init__(factor_name = 'umd_ratio_zsj',
                                              required_columns = ['close_zz500'],
                                              lookback_bars = 1400)

    def on_bar(self, data):
        ##### def data #####
        stk_close = data['close_zz500']
        factor_name = 'umd_ratio_zsj'
        stk_ret = stk_close / stk_close.shift(1) - 1
        up_mask = stk_ret > 0
        down_mask = stk_ret < 0
        stk_up_cnt = up_mask.sum(axis=1)
        stk_down_cnt = down_mask.sum(axis=1)
        umd_ratio_raw = (stk_up_cnt - stk_down_cnt) / (stk_up_cnt + stk_down_cnt)
        ma_win = 160
        ts_pct_win = 1200
        umd_ratio = calc_ma_helper(umd_ratio_raw, ma_win, ts_pct_win)
        ##### format factor #####
        factor = pd.DataFrame(umd_ratio,columns=[self.__class__.__name__])
        return factor


