# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 19:58:06 2021

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
class Short_BS_Main_CFG4_CC(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_smallorder_money','buy_midorder_money','weight', 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_close = data['close'].values[-21:]
        stk_weight = data['weight'].values[-1]
  
        df_s = np.nansum(data['buy_smallorder_money'].fillna(0).values[-5:] + data['buy_midorder_money'].fillna(0).values[-5:], axis = 0) * stk_weight

        hret = ts_pct_change(stk_close, 1)
        hret = np.nanmean(hret[-20:], axis = 0)
        
        df_s_mask = np.nanmedian(df_s)
        df_s_mask = np.expand_dims(df_s_mask, axis = -1)
        hret_1 = ma.array(hret, mask=(df_s<=df_s_mask))
        hret_2 = ma.array(hret, mask=(df_s>=df_s_mask))
        temp2 = np.nanmean(hret_1) - np.nanmean(hret_2)
        return temp2
