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

class ret_a2p_sharpe_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(ret_a2p_sharpe_zsj, self).__init__(factor_name = 'ret_a2p_sharpe_zsj',
                                              required_columns = ['close_zz500','amount_zz500', 'weight_boolean_zz500'],
                                              lookback_bars = 3000)

    def on_bar(self, data):
        ##### def data #####
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500'][bool_mask]
        stk_ret = (stk_close / stk_close.shift(1) - 1)[bool_mask]
        ma_win = 30
        ts_pct_win = 2400
        roll_win = 10
        min_win = int(roll_win * 0.5)
        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0
        ret_active_raw = stk_ret[active_mask].mean(axis=1)
        ret_inactive_raw = stk_ret[inactive_mask].mean(axis=1)
        
        a = ret_active_raw.rolling(roll_win,min_win).std()
        a[abs(a)<1e-8] = np.nan
        b = ret_inactive_raw.rolling(roll_win, min_win).std()
        b[abs(b) < 1e-8] = np.nan
        ret_active_sharpe_raw = ret_active_raw.rolling(roll_win, min_win).mean() / a
        ret_inactive_sharpe_raw = ret_inactive_raw.rolling(roll_win, min_win).mean() / b
        ret_a2p_sharpe_raw = ret_active_sharpe_raw - ret_inactive_sharpe_raw
        ret_a2p_sharpe = calc_ma_helper(ret_a2p_sharpe_raw, ma_win, ts_pct_win)
        ##### format factor #####
        factor = pd.DataFrame(ret_a2p_sharpe,columns=[self.__class__.__name__])
        return factor


