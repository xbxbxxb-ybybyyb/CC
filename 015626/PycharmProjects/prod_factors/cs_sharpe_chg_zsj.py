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

class cs_sharpe_chg_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(cs_sharpe_chg_zsj, self).__init__(factor_name = 'cs_sharpe_chg_zsj',
                                                required_columns = ['close_zz500'],
                                                lookback_bars = 3600)

    def on_bar(self, data):
        ##### def data #####
        stk_close = data['close_zz500']
        stk_ret = stk_close / stk_close.shift(1) - 1
        factor_name = 'cs_sharpe_chg'
        ma_win = 180
        ts_pct_win = 2400
        short_win = 20
        long_win = 240
        cs_ret = stk_ret.mean(axis=1)
        cs_std = stk_ret.std(axis=1)
        cs_sharpe_raw = cs_ret / cs_std
        cs_sharpe = calc_ma_helper(cs_sharpe_raw, ma_win, ts_pct_win)
        cs_sharpe_chg = calc_change_helper(cs_sharpe, short_win, long_win, ts_pct_win)
        ##### format factor #####
        factor = pd.DataFrame(cs_sharpe_chg,columns=[self.__class__.__name__])
        return factor


