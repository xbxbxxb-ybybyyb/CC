# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 14:37:54 2022

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk

def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))


class HL_SELECT_CC(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'high', 'low', 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        hclose = data['close'].values[-61:]
        hret = hclose[1:]/hclose[:-1] - 1
        hret = ts_truncated_ema_span_1(hret, 60, 10)
        df_s = np.nanmax(data['high'].values[-60:], axis = 0)/ (np.nanmin(data['low'].values[-60:], axis = 0)) * data['weight'].values[-1]    
        hret = hret[-1]
        try:
            df_s_mask = np.nanmedian(df_s)
            df_s_mask = np.expand_dims(df_s_mask, axis = -1)
            hret_1 = ma.array(hret, mask=(df_s<=df_s_mask))
            hret_2 = ma.array(hret, mask=(df_s>=df_s_mask))
            temp2 = np.nanmean(hret_1) - np.nanmean(hret_2)
        except:
            temp2 = np.nan
        return temp2