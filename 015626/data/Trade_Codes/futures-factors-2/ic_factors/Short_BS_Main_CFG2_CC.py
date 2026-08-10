# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 17:53:38 2021

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *

class Short_BS_Main_CFG2_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['stk_index_corr_zz500', 'BuyUniqueOrderNum', 'BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):

        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-3:]
        stk_BuyTradeNum = data['BuyTradeNum'].values[-3:]
        stk_SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-3:]
        stk_SellTradeNum = data['SellTradeNum'].values[-3:]

        df_s = data['stk_index_corr_zz500'].values[-3:]
        amount_mask = np.nanquantile(df_s, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        factor_raw = (stk_BuyUniqueOrderNum / r(stk_BuyTradeNum)) - (stk_SellUniqueOrderNum / r(stk_SellTradeNum))
        factor_raw_after_mask = ma.array(factor_raw, mask=(df_s<=amount_mask))
        factor_raw_after_mask = np.nanmean(factor_raw_after_mask, axis=1)
        factor_mean = np.nanmean(factor_raw_after_mask)
        return -factor_mean
