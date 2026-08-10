# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 18:19:27 2021

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk

class StB_CC_IF_IH(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_bigorder_count', 'buy_smallorder_count','buy_midorder_count','buy_bigorder_count', 'buy_superorder_count', 'weight']
    normalize_size = 2400
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):

        stk_buy_superorder_count = data['buy_superorder_count'].fillna(0).values[-10:]
        stk_buy_bigorder_count = data['buy_bigorder_count'].fillna(0).values[-10:]
        stk_buy_midorder_count = data['buy_midorder_count'].fillna(0).values[-10:]
        stk_buy_smallorder_count = data['buy_smallorder_count'].fillna(0).values[-10:]
        stk_sell_bigorder_count = data['sell_bigorder_count'].fillna(0).values[-10:]
        stk_weight = data['weight'].values[-10:]

        alll = r(stk_buy_superorder_count + stk_buy_bigorder_count + stk_buy_midorder_count + stk_buy_smallorder_count)
        temp2 = stk_sell_bigorder_count / alll
        temp = np.nanmean(temp2 * stk_weight, axis = 1)
        factor_mean = np.nanmean(temp)
        return factor_mean