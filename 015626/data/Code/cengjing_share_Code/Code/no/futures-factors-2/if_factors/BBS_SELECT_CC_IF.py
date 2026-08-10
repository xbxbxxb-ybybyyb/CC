# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 19:10:08 2022

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


class BBS_SELECT_CC_IF(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyNumOrdersSumMean', 'SellNumOrdersSumMean', 'WeightSellOrderQtySumMean', 'WeightBuyOrderQtySumMean','BuyUniqueOrderNum','BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        factor_raw = (data['BuyUniqueOrderNum'].values[-2:] / r(data['BuyTradeNum']).values[-2:]) - (data['SellUniqueOrderNum'].values[-2:] / r(data['SellTradeNum'].values[-2:]))
        
        df_s1 = bk.move_mean((data['BuyNumOrdersSumMean'].values[-21:]/ r(data['WeightBuyOrderQtySumMean'].values[-21:])), 20, 19, axis = 0)
        df_s2 = bk.move_mean((data['SellNumOrdersSumMean'].values[-21:]/ r(data['WeightSellOrderQtySumMean'].values[-21:])), 20, 19, axis = 0)
        df_s = (df_s1 + df_s2)[-2:]

        amount_mask = np.nanquantile(df_s, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        
        factor_raw_after_mask = ma.array(factor_raw, mask=(df_s<=amount_mask))
        factor_raw_after_mask = np.nanmean(factor_raw_after_mask, axis=1)
        factor_mean = np.nanmean(factor_raw_after_mask)
        return -factor_mean
