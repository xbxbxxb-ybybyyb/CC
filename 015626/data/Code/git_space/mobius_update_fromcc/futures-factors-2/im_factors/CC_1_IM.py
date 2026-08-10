# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 15:19:43 2022

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

class CC_1_IM(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount','volume','weight', 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        
        amount = data['amount'].values[-36:]
        volume = data['volume'].values[-36:]
        hclose = data['close'].values[-136:]
        weight = data['weight'].values[-36:]
        
        a = bk.move_sum(amount, 20, 2, axis = 0)/r(bk.move_sum(volume, 20, 2, axis = 0))
        b = bk.move_mean(amount/r(volume), 20, 2, axis = 0)
        factor = (a/r(b) * weight)[-1]
        hret = ts_pct_change(hclose, 1)
        hret[abs(hret)>10000] = np.nan
        hret = ts_truncated_ema_span_1(hret, 120, 10)[-1]
        
        df_s_mask = np.nanmedian(factor)
        df_s_mask = np.expand_dims(df_s_mask, axis = -1)
        hret_1 = ma.array(hret, mask=(factor<=df_s_mask))
        hret_2 = ma.array(hret, mask=(factor>=df_s_mask))
        temp2 = np.nanmean(hret_1) - np.nanmean(hret_2)

        return temp2