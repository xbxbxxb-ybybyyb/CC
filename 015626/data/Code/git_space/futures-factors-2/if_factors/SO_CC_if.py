# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 18:57:57 2021

@author: appadmin
"""
from operators_wsc_1_0 import *
import numpy.ma as ma
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))

class SO_CC_if(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'buy_superorder_money', 'close']
    normalize_size = 2400
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_close = data['close'].values[-420:]
        stk_weight = data['weight'].values[-420:]

        stk_superorder_count = data['buy_superorder_money'].fillna(0).values[-420:]
        
        
        df_s = (ts_truncated_ema_span_1(stk_superorder_count, 400, 120))[-1] * stk_weight[-1]

        hret = ts_pct_change(stk_close, 1)[-110:]
        hret[abs(hret)>10000] = np.nan
        hret = ts_truncated_ema_span_1(hret, 100, 20)[-1]
        df_s_mask = np.nanmedian(df_s)
        df_s_mask = np.expand_dims(df_s_mask, axis = -1)
        hret_1 = ma.array(hret, mask=(df_s<=df_s_mask))
        hret_2 = ma.array(hret, mask=(df_s>=df_s_mask))
        temp2 = np.nanmean(hret_1) - np.nanmean(hret_2)

        return temp2