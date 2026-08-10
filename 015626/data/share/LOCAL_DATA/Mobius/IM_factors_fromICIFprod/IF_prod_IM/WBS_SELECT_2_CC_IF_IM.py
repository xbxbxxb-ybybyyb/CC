# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 18:55:11 2022

@author: appadmin
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 19:12:22 2021

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk


class WBS_SELECT_2_CC_IF_IM(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['WeightSellOrderQtySumMean', 'WeightBuyOrderQtySumMean','BuyUniqueOrderNum','BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        factor_raw = (data['BuyUniqueOrderNum'].values[-5:] / r(data['BuyTradeNum']).values[-5:]) - (data['SellUniqueOrderNum'].values[-5:] / r(data['SellTradeNum'].values[-5:]))
        df_s = (data['WeightBuyOrderQtySumMean'].values[-5:] / r(data['WeightSellOrderQtySumMean'].values[-5:]))
        
        amount_mask = np.nanquantile(df_s, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
       
        factor_raw_after_mask = ma.array(factor_raw, mask=(df_s<=amount_mask))
        factor_raw_after_mask = np.nanmean(factor_raw_after_mask, axis=1)
        factor_mean = np.nanmean(factor_raw_after_mask)
        return -factor_mean
