# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 17:50:54 2022

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
from operators_wsc_1_0 import *

class wsc_fast5_hf(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['SellTradeNum', 'SellUniqueOrderNum', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    handle_preadj = False
    
    def calculate(self, data):
        
        factor_raw = np.nansum(data['SellUniqueOrderNum'].values[-5:]*data['weight'].values[-5:], axis = 1) / \
                      r(np.nansum(data['SellTradeNum'].values[-5:]*data['weight'].values[-5:], axis = 1))
        factor_mean = np.nansum(factor_raw)

        return factor_mean
