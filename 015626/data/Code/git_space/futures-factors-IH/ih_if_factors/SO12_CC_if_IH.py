# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 09:43:18 2021

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

class SO12_CC_if_IH(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_superorder_count','weight', 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):

        stk_close = data['close'].values[-107:]
        stk_weight = data['weight'].iloc[-107:]
        
        bool_df = stk_weight.gt(pd.Series(stk_weight.quantile(0.8, axis = 1)), axis=0)
        
        factor_raw = (data['buy_superorder_count'].iloc[-107:].fillna(0)[bool_df]).values
        
        df_s = (ts_truncated_ema_span_1(factor_raw, 100, 20)*stk_weight)[-2:]

        hret = ts_pct_change(stk_close, 1)
        hret = (ts_truncated_ema_span_1(hret, 100, 20))[-2:]
        
        df_s_mask = np.nanmedian(df_s, axis = 1)
        df_s_mask = np.expand_dims(df_s_mask, axis=-1)
        hret_1 = ma.array(hret, mask=(df_s<=df_s_mask))
        hret_2 = ma.array(hret, mask=(df_s>=df_s_mask))
        temp2 = np.nanmean(hret_1, axis = 1) - np.nanmean(hret_2, axis = 1)
        
        return temp2[-1]
