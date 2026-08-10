# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 09:50:16 2022

@author: appadmin
"""

from future_factor import FutureFactor
import numpy as np
import numpy.ma as ma
import pandas as pd
from operators_wsc_1_0 import *
from operators_cc import *
from scipy.stats import skew





class sn_to_on_w_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'SellTradeNum', 'lo_counts', 'weight']
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        
        d1 = (data['lo_counts'].values[-1])
        
        
        temp = np.nansum(data['weight'].values[-1] * ( data['SellTradeNum'].values[-1]) / r(d1))
        
        
        return temp

