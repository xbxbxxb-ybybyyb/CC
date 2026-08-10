# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 10:54:12 2022

@author: appadmin
"""

from future_factor import FutureFactor
import numpy as np
import pandas as pd
from operators_wsc_1_0 import *
from operators_cc import *
from scipy.stats import skew

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


class WBS_Sharpe_CC_IF(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'WeightBuyOrderQtySumMean', 'WeightSellOrderQtySumMean', 'close']
    normalize_size = 2000
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        weight = data['weight'].values[-40:]
        w = data['WeightBuyOrderQtySumMean'].values[-40:] / data['WeightSellOrderQtySumMean'].values[-40:]
        #* data_dict['volume_300']
        df_s = np.nanmean(w, axis = 0) / np.nanstd(w, axis = 0)

        
        hclose = data['close'].iloc[-460:]
        hret = ts_pct_change(hclose, 1)
        hret[abs(hret)>10000] = np.nan
        hret = hret.ewm(40).mean().values[-1]# * weight[-1]
        df_s_mask = np.nanmedian(df_s)
        df_s_mask = np.expand_dims(df_s_mask, axis = -1)
        hret_1 = np.ma.array(hret, mask=(df_s<=df_s_mask))
        hret_2 = np.ma.array(hret, mask=(df_s>=df_s_mask))
        temp2 = np.nanmean(hret_1) - np.nanmean(hret_2)
        return -temp2