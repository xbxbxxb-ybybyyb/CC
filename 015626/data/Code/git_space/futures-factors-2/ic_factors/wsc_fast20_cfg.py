# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 17:29:40 2022

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
from operators_wsc_1_0 import *

class wsc_fast20_cfg(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'amount', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.9,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].iloc[-37:]
        stk_index_corr = data['amount'].iloc[-37:]
        stk_index_corr_rank_mask = 2 * section_rank_np(stk_index_corr.values, pct=True) - 1
        N = 20
        dpo = stk_close - ts_delay(ts_mean(stk_close, N), int(N/2+1))
        factor_raw = np.nansum(dpo.values * stk_index_corr_rank_mask, axis=1)

        return factor_raw[-1]