# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 11:16:36 2022

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


class Short_BSS_CC_IF(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'close', 'BuyNumOrdersSumMean', 'WeightBuyOrderQtySumMean', 'SellNumOrdersSumMean', 'WeightSellOrderQtySumMean', 'weight']
    normalize_size = 2000
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        df_s1 = ((data['BuyNumOrdersSumMean'].iloc[-40:] / r(data['WeightBuyOrderQtySumMean'].iloc[-40:])))#*data['weight_500']
        df_s2 = ((data['SellNumOrdersSumMean'].iloc[-40:] / r(data['WeightSellOrderQtySumMean'].iloc[-40:])))#*data['weight_500']
        df_s11 = (df_s1.skew(axis = 0).values)*data['weight'].values[-1]
        df_s22 = (df_s2.skew(axis = 0).values)*data['weight'].values[-1]
        ccc1 = df_s11 + df_s22
        hclose = data['close'].iloc[-230:]
        hret = ts_pct_change(hclose, 1)
        hret[abs(hret)>10000] = np.nan
        hret = hret.ewm(8).mean().values[-1]
        ccc1_mask = np.expand_dims(np.nanmedian(ccc1), axis=-1)
        hret1 = np.ma.array(hret, mask=(ccc1<=ccc1_mask))
        hret2 = np.ma.array(hret, mask=(ccc1>=ccc1_mask))
        cc2 = np.nanmean(hret1) - np.nanmean(hret2)
        return cc2


