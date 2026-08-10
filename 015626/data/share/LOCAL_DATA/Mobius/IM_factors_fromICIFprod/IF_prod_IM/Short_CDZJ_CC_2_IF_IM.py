# -*- coding: utf-8 -*-
"""
Created on Sun May 15 19:26:37 2022

@author: appadmin
"""
import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk
from scipy.stats import skew

def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))

class Short_CDZJ_CC_2_IF_IM(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'SellTradeNum', 'weight', 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank' 

    handle_preadj = False
    
    def calculate(self, data):
        
        cl = data['close'].values[-125:]
        ret = cl[1:] - cl[:-1]
        temp_rsi2 = (ret<0)
        temp_rsi1 = (ret>0)
        amount = data['amount'].values[-124:]
        btn = data['SellTradeNum'].values[-124:]
        a = 120
        b = 45
     
        temp2 = bk.move_sum(amount, a, 5, axis = 0)[-2:]/r(bk.move_sum(btn, a, 5, axis = 0))[-2:]
        temp1 = bk.move_sum(temp_rsi2*amount, a, 5, axis = 0)[-2:]/r(bk.move_sum(temp_rsi2*btn, a, 5, axis = 0))[-2:]
        
        temp11 = bk.move_sum(temp_rsi1*amount, a, 5, axis = 0)[-2:]/r(bk.move_sum(temp_rsi1*btn, a, 5, axis = 0))[-2:]
        
        temp = ((temp1 - temp11)/r(temp2))
        
        hret = cl[1:] / cl[:-1] - 1
        hret[abs(hret)>10000] = np.nan
        hret = ts_truncated_ema_span_1(hret, 120, b)[-2:]*(data['weight'].values[-2:])
        
        df_s_mask = np.nanmedian(temp, axis=1)
        
        df_s_mask = np.expand_dims(df_s_mask, axis=-1)

        hret_1 = ma.array(hret, mask=(temp<=df_s_mask))

        hret_2 = ma.array(hret, mask=(temp>=df_s_mask))
        
        temp2 = np.nanmean(hret_1, axis=1) - np.nanmean(hret_2, axis=1)
        
        return temp2[-1]