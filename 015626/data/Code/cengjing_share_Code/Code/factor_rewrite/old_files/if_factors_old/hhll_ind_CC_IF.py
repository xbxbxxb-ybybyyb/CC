# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:49:40 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    


class hhll_ind_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
       
        hhigh = data['high_000300.SH'].iloc[-121:]
        hlow = data['low_000300.SH'].iloc[-121:]
        temp = np.where((hhigh>hhigh.shift(1)) & (hlow>hlow.shift(1)), 4, np.where((hhigh<hhigh.shift(1)) & (hlow<hlow.shift(1)), 0, 1))
        
        return np.abs(np.nanmean(temp[-120:]))