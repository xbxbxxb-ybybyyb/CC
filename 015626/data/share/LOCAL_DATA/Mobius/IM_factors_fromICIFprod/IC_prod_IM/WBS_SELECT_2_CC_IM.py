# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 14:00:14 2022

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


class WBS_SELECT_2_CC_IM(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight','BuyNumOrdersSumMean', 'SellNumOrdersSumMean', 'WeightSellOrderQtySumMean', 'WeightBuyOrderQtySumMean','BuyUniqueOrderNum','BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        factor_raw1 = np.nansum(data['BuyUniqueOrderNum'].values[-2:], axis = 0) / r(np.nansum(data['BuyTradeNum'].values[-2:], axis = 0))
        factor_raw2 = np.nansum(data['SellUniqueOrderNum'].values[-2:], axis = 0) / r(np.nansum(data['SellTradeNum'].values[-2:], axis = 0))
        factor_raw = factor_raw1 - factor_raw2
        df_s1 = np.nanmean(data['BuyNumOrdersSumMean'].values[-15:], axis = 0) / r(np.nansum(data['WeightBuyOrderQtySumMean'].values[-15:], axis = 0))#*data['weight_300']
        df_s2 = np.nanmean(data['SellNumOrdersSumMean'].values[-15:], axis = 0) / r(np.nansum(data['WeightSellOrderQtySumMean'].values[-15:], axis = 0))#*data['weight_300']
        df_s = (df_s1 + df_s2)*data['weight'].values[-1]
        
        amount_mask = np.nanquantile(df_s, 0.8)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        
        factor_raw_after_mask = ma.array(factor_raw, mask=(df_s<=amount_mask))
        factor_raw_after_mask = np.nanmean(factor_raw_after_mask)
        return -factor_raw_after_mask
