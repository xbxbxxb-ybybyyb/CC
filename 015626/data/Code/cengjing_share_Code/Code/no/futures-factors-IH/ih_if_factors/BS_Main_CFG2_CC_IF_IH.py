# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 19:36:22 2021

@author: appadmin
"""
import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk

class BS_Main_CFG2_CC_IF_IH(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum', 'weight']
    normalize_size = 240
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):

        df_s = data['weight'].values[-13:]
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-13:]
        stk_BuyTradeNum = data['BuyTradeNum'].values[-13:]

        amount_mask = np.nanquantile(df_s, 0.8, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        factor_raw = (stk_BuyUniqueOrderNum / r(stk_BuyTradeNum))# - (stk_SellUniqueOrderNum / r(stk_SellTradeNum))
        factor_raw_after_mask = ma.array(factor_raw, mask=(df_s<=amount_mask))
        factor_raw_after_mask = np.nanmean(factor_raw_after_mask, axis=1)
        factor_mean = np.nanmean(factor_raw_after_mask[-2:])
        return -factor_mean
