# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 14:20:13 2022

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
from operators_wsc_1_0 import *
import pandas as pd
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

class CC_0_IM(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'WeightBuyOrderQtySumMean', 'WeightSellOrderQtySumMean', 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        df_s = np.nanmean(data['WeightBuyOrderQtySumMean'].values[-10:] / r(data['WeightSellOrderQtySumMean'].values[-10:]),  axis = 0)
        df_s = df_s * data['weight'].values[-1]
        hclose = data['close'].values[-121:]
        hret = hclose[1:]/hclose[:-1] - 1
        hret[abs(hret)>10000] = np.nan
        hret = ts_truncated_ema_span_1(hret, 120, 10)[-1]
        df_s_mask = np.nanmedian(df_s)
        df_s_mask = np.expand_dims(df_s_mask, axis=-1)
        hret_1 = np.ma.array(hret, mask=(df_s<=df_s_mask))
        hret_2 = np.ma.array(hret, mask=(df_s>=df_s_mask))
        temp2 = np.nanmean(hret_1) - np.nanmean(hret_2)

        return temp2