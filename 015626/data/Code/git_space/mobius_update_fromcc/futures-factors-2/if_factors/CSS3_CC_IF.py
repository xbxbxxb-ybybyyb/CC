# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 15:59:13 2023

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


class CSS3_CC_IF(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'buy_bigorder_count_othermin', 'buy_midorder_money_othermin', 'weight', 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        
        temp1 = data['buy_bigorder_count_othermin'].values[-20:]
        temp2 = data['buy_midorder_money_othermin'].values[-20:]
        
        hclose = data['close'].iloc[-120:]
        weight = data['weight'].values[-1]
        
        df_s1 = np.nanmean(temp1, axis = 0)
        df_s2 =  np.nanmean(temp2, axis = 0)
        df_s =  weight * df_s1 / r(df_s2)
        
        hret = (hclose/hclose.shift(1) - 1)
        hret[abs(hret)>10000] = np.nan

        hret = hret.ewm(20, min_periods = 1).mean().values[-1]
        
        try:
            df_s_mask = np.nanmedian(df_s)
            df_s_mask = np.expand_dims(df_s_mask, axis=-1)
            hret_1 = ma.array(hret, mask=(df_s<=df_s_mask))
            hret_2 = ma.array(hret, mask=(df_s>=df_s_mask))
            temp2 = np.nanmean(hret_1) - np.nanmean(hret_2)
        except:
            temp2 = np.nan
        
        
        return temp2

