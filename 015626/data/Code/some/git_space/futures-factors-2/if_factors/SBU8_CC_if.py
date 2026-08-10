# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 15:32:03 2021

@author: appadmin
"""
import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk

class SBU8_CC_if(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum', 'weight']
    normalize_size = 360
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-124:]
        stk_BuyTradeNum = data['BuyTradeNum'].values[-124:]
        stk_weight = data['weight'].values[-3:]
        
        a = stk_BuyUniqueOrderNum / r(stk_BuyTradeNum)

        temp1 = (bk.move_max(a, 120, 15, axis=0) - a) / (bk.move_max(a, 120, 15, axis=0) - bk.move_min(a, 120, 15, axis=0))
        temp2 = (a - bk.move_min(a, 120, 15, axis=0)) / (bk.move_max(a, 120, 15, axis=0) - bk.move_min(a, 120, 15, axis=0))
        
        factor = (temp2 - temp1)[-3:]
        factor = np.nanmean(factor * stk_weight, axis=1)
        factor = -bk.move_mean(factor, 2, 1)
        return factor[-1]