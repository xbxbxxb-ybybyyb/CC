# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 11:04:43 2022

@author: appadmin
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 15:24:24 2022

@author: appadmin
"""

from future_factor import FutureFactor
import numpy as np
import pandas as pd
from operators_wsc_1_0 import *
from operators_cc import *

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


class BuySellP_1_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'WeightBuyOrderQtySumMean', 'WeightSellOrderQtySumMean', 'weight']
    normalize_size = 4800
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        w = (data['WeightBuyOrderQtySumMean'].values[-15:]) / r(data['WeightSellOrderQtySumMean'].values[-15:])
        df_s = np.nanmax(w, axis = 0)/r(np.nanmin(w, axis = 0))
        df_s = df_s * data['weight'].values[-1]
        hclose = data['close'].iloc[-131:]
        hret = hclose/hclose.shift(1)-1
        hret[abs(hret)>10000] = np.nan
        hret = hret.ewm(4).mean().values[-1]
        df_s_mask = np.nanmedian(df_s)
        df_s_mask = np.expand_dims(df_s_mask, axis=-1)
        hret_1 = np.ma.array(hret, mask=(df_s<=df_s_mask))
        hret_2 = np.ma.array(hret, mask=(df_s>=df_s_mask))
        temp2 = np.nanmean(hret_1) - np.nanmean(hret_2)
        
        return temp2