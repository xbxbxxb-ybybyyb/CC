# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 13:11:18 2022

@author: appadmin
"""
import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
from operators_wsc_1_0 import *
import pandas as pd

#
def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))

class BSW_1_CC_IM(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'WeightBuyOrderQtySumMean', 'WeightSellOrderQtySumMean','BuyNumOrdersSumMean','SellNumOrdersSumMean', 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        df_s1 = bk.move_mean(data['BuyNumOrdersSumMean'].values[-52:] / r(data['WeightBuyOrderQtySumMean'].values[-52:]), 20, 2, axis = 0)
                 
        df_s2 = bk.move_mean(data['SellNumOrdersSumMean'].values[-52:] / r(data['WeightSellOrderQtySumMean'].values[-52:]), 20, 2, axis = 0)
        
        df_s = ((df_s1 + df_s2)[-30:])*(data['weight'].values[-30:])
        
        hclose = data['close'].values[-50:]
        hret = hclose[1:]/hclose[:-1] - 1
        hret[abs(hret)>10000] = np.nan
        hret = ts_truncated_ema_span_1(hret, 40, 5)[-30:]
        
        df_s_mask = np.nanmedian(df_s, axis = 1)
        df_s_mask = np.expand_dims(df_s_mask, axis=-1)
        hret_1 = ma.array(hret, mask=(df_s<=df_s_mask))
        hret_2 = ma.array(hret, mask=(df_s>=df_s_mask))
        temp2 = np.nanmean(hret_1, axis = 1) - np.nanmean(hret_2, axis = 1)
        
        temp2 = ts_truncated_ema_span_1(temp2, 15, 3)[-1]
        
        return temp2