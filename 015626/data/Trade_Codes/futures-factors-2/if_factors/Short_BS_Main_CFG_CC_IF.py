# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 17:12:17 2021

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



class Short_BS_Main_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'BuyUniqueOrderNum', 'BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 

    handle_preadj = False
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-157:]

        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-126:]
        stk_BuyTradeNum = data['BuyTradeNum'].values[-126:]
        stk_SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-126:]
        stk_SellTradeNum = data['SellTradeNum'].values[-126:]

        df_s = bk.move_sum(stk_amount, 30, 5, axis=0)[-126:]

        
        amount_mask = np.nanquantile(df_s, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        factor_raw = (stk_BuyUniqueOrderNum / r(stk_BuyTradeNum)) - (stk_SellUniqueOrderNum / r(stk_SellTradeNum))
        factor_raw_after_mask = ma.array(factor_raw, mask=(df_s<=amount_mask))
        factor_raw_after_mask = np.nanmean(factor_raw_after_mask, axis=1)
        factor_mean = ts_truncated_ema_span_1(factor_raw_after_mask, 120, 4)
        return -factor_mean[-1]