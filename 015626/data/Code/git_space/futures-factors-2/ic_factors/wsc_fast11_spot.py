# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 17:12:18 2022

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
from operators_wsc_1_0 import *

class wsc_fast11_spot(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, data):

        index_open = data['open_000905.SH'].values[-30:]
        index_high = data['high_000905.SH'].values[-30:]
        index_close = data['close_000905.SH'].values[-30:]
        index_low = data['low_000905.SH'].values[-30:]
        
        x = index_high - index_low
        x[abs(x)<1e-8] = np.nan
        ratio1 = (index_close-index_open) / x
        ratio1[(index_close-index_open)<0] = 0
        factor_mean = np.nanmean(ratio1)
        
        return factor_mean