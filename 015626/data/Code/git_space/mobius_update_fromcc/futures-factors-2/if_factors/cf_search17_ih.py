# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 11:10:07 2022

@author: appadmin
"""

### 
from future_factor import FutureFactor
import numpy as np
import pandas as pd
from operators_wsc_for_srch import *
from operators_cc import *
from scipy.stats import skew


class cf_search17_ih(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_midorder_count', 'BuyUniqueOrderNum',  'SellUniqueOrderNum', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        bbn_3_to_bun_w = np.nansum(data['buy_midorder_count'].values[-26:] * data['weight'].values[-26:] / r(data['BuyUniqueOrderNum'].values[-26:]), axis = 1)
        
        bun_r = np.nansum(data['BuyUniqueOrderNum'].values[-220:], axis = 1) / r(np.nansum(data['BuyUniqueOrderNum'].values[-220:] + data['SellUniqueOrderNum'].values[-220:], axis = 1))
        
        temp1 = midpoint(ts_position(bun_r, 55), 30)[-1]
        
        temp2 = coefficient_of_variation(bbn_3_to_bun_w, 25)[-1]
        
        factor_raw = -temp1 * temp2
        
        return factor_raw


