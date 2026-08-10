# -*- coding: utf-8 -*-
"""
Created on Tue Nov 30 14:27:51 2021

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma

def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))

class BO3_CC_if(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_bigorder_money','weight', 'close']
    normalize_size = 2400
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_close = data['close'].values[-107:]
        stk_weight = data['weight'].values[-107:]

        stk_buy_bigorder_count = data['buy_bigorder_money'].fillna(0).values[-107:]
        
        
        df_s = ts_truncated_ema_span_1(stk_buy_bigorder_count, 100, 10)*stk_weight

        hret = ts_pct_change(stk_close, 1)
        hret = ts_truncated_ema_span_1(hret, 100, 10)
        
        df_s_mask = np.nanmedian(df_s, axis=1)
        df_s_mask = np.expand_dims(df_s_mask, axis=-1)
        hret_1 = ma.array(hret, mask=(df_s<=df_s_mask))
        hret_2 = ma.array(hret, mask=(df_s>=df_s_mask))
        temp2 = np.nanmean(hret_1, axis=1) - np.nanmean(hret_2, axis=1)
        return temp2[-1]