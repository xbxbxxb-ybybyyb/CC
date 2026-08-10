# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 15:51:30 2021

@author: appadmin
"""
import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk

class SO10_CC_if_IM(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'buy_bigorder_count', 'buy_superorder_count', 'buy_smallorder_count', 'buy_midorder_count']
    normalize_size = 240
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_amount = data['weight'].values[-23:]
        stk_buy_superorder_count = data['buy_superorder_count'].fillna(0).values[-23:]
        stk_buy_bigorder_count = data['buy_bigorder_count'].fillna(0).values[-23:]
        stk_buy_midorder_count = data['buy_midorder_count'].fillna(0).values[-23:]
        stk_buy_smallorder_count = data['buy_smallorder_count'].fillna(0).values[-23:]


        amount_mask = np.nanquantile(stk_amount, 0.7, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        alll = r(stk_buy_superorder_count + stk_buy_bigorder_count + stk_buy_midorder_count + stk_buy_smallorder_count)
        temp2 = stk_buy_superorder_count / alll
        temp2_after_mask = ma.array(temp2, mask=(stk_amount<=amount_mask))
        factor_raw = np.nanmean(temp2_after_mask, axis=1)
        factor_mean = np.nanmean(factor_raw[-20:])
        return factor_mean