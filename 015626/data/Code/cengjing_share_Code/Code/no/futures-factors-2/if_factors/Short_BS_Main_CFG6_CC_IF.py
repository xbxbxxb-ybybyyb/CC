# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 15:38:27 2021

@author: appadmin
"""


import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import *
from future_factor import FutureFactor


def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))

class Short_BS_Main_CFG6_CC_IF(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['WeightBuyOrderQtySumMean', 'WeightSellOrderQtySumMean',  'close', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 

    handle_preadj = False
    
    def calculate(self, data):
        
        a = (data['WeightBuyOrderQtySumMean'].iloc[-140:].values/r(data['WeightSellOrderQtySumMean'][-140:]).values)*data['weight'].iloc[-140:].values
        
        stk_close = data['close'].values[-270:]
        hret = stk_close[1:]/stk_close[:-1] - 1
        hret[abs(hret)>10000] = np.nan
        hret = ts_truncated_ema_span_1(hret, 120, 4)[-140:]
        df_s_mask = np.nanmedian(a, axis=1)
        
        df_s_mask = np.expand_dims(df_s_mask, axis=-1)

        hret_1 = ma.array(hret, mask=(a<=df_s_mask))

        hret_2 = ma.array(hret, mask=(a>=df_s_mask))
        
        temp2 = np.nanmean(hret_1, axis=1) - np.nanmean(hret_2, axis=1)
        factor = ts_truncated_ema_span_1(temp2, 120, 15)[-1]
       
        return factor