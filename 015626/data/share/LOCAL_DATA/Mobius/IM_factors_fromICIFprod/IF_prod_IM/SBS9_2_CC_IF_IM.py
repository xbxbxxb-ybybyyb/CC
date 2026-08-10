# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 15:31:38 2021

@author: appadmin
"""
import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class SBS9_2_CC_IF_IM(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_superorder_money',  'sell_bigorder_money', 'sell_midorder_money', 'sell_smallorder_money']
    normalize_size = 720
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        a = data['sell_superorder_money'][-5:].fillna(0) + data['sell_bigorder_money'][-5:].fillna(0) + data['sell_midorder_money'][-5:].fillna(0) + data['sell_smallorder_money'][-5:].fillna(0)
        temp2 = (data['sell_bigorder_money'][-5:].fillna(0) + data['sell_superorder_money'][-5:].fillna(0))/ a.replace(0, np.nan)
        temp2 = temp2.replace([-np.inf, np.inf], np.nan)
        factor = np.nanmean(temp2.values,axis = 1)
        factor = np.nanmean(factor)
        
        return factor