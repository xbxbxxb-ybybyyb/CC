# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 17:09:16 2022

@author: appadmin
"""

### 
from future_factor import FutureFactor
import numpy as np
import numpy.ma as ma
import pandas as pd
from operators_wsc_1_0 import *
from operators_cc import *
from scipy.stats import skew



class bn_to_on_ic(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'BuyTradeNum', 'lo_counts']
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        
        d1 = (np.nansum(data['lo_counts'].values[-1])) 
        
        if abs(d1) <= 1e-9:
            d1 = np.nan
        
        temp = np.nansum((data['BuyTradeNum'].values[-1]) ) / d1
        
        
        return temp

