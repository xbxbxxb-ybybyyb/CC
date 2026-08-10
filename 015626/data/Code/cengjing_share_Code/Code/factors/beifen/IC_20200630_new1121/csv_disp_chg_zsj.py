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

class csv_disp_chg_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(csv_disp_chg_zsj, self).__init__(factor_name = 'csv_disp_chg_zsj',
                                              required_columns = ['close_zz500', 'weight_boolean_zz500'],
                                              lookback_bars = 2400)

    def on_bar(self, data):
        ##### def data #####
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_ret = (stk_close / stk_close.shift(1) - 1)[bool_mask]
        factor_name = 'csv_disp_chg_zsj'
        ma_win = 60
        short_win = 20
        long_win = 240
        ts_pct_win = 1200
        csv_disp = stk_ret.std(axis=1)
        stk2idx_ret = stk_ret.mean(axis=1)
        csv_disp_sign_raw = csv_disp * np.sign(stk2idx_ret)
        csv_disp_sign = calc_ma_helper(csv_disp_sign_raw, ma_win, ts_pct_win)
        csv_disp_chg = calc_change_helper(csv_disp_sign, short_win, long_win, ts_pct_win)
        ##### format factor #####
        factor = pd.DataFrame(csv_disp_chg,columns=[self.__class__.__name__])
        return factor


