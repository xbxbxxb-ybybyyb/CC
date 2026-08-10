# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 17:45:46 2022

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
from operators_wsc_1_0 import *

class wsc_fast4_hf(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['BuyTradeNum', 'BuyUniqueOrderNum', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    handle_preadj = False
    
    def calculate(self, data):
        
        factor_raw = np.nansum(data['BuyTradeNum'].values[-3:]*data['weight'].values[-3:], axis = 1) / \
                      r(np.nansum(data['BuyUniqueOrderNum'].values[-3:]*data['weight'].values[-3:], axis = 1))
        factor_mean = np.nansum(factor_raw)

        return factor_mean