# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 13:45:54 2022

@author: appadmin
"""
import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
from operators_wsc_1_0 import *

def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))
    
class Short_BS_Main_CFG3_CC(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_bigorder_money','buy_superorder_money','weight', 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_close = data['close'].values[-90:]
        stk_weight = data['weight'].values[-1]
  
        df_s = np.nansum(data['buy_superorder_money'].fillna(0).values[-10:] + data['buy_bigorder_money'].fillna(0).values[-10:], axis = 0) * stk_weight

        hret = stk_close[1:]/stk_close[:-1] - 1
        hret[abs(hret) > 100000] = np.nan
        hret = ts_truncated_ema_span_1(hret, 60, 15)[-1]
        
        df_s_mask = np.nanmedian(df_s)
        df_s_mask = np.expand_dims(df_s_mask, axis=-1)
        hret_1 = ma.array(hret, mask=(df_s<=df_s_mask))
        hret_2 = ma.array(hret, mask=(df_s>=df_s_mask))
        temp2 = pd.Series(hret_1).mean() - pd.Series(hret_2).mean()
        
        return temp2