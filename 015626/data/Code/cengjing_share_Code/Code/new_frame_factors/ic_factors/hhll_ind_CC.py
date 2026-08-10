# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:07:48 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class hhll_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high', 'low']}  
    normalize_size = 2420
    normalize_type = 'ts_rank'
    #num_range = [-0.499999, 1]
    
    def calculate(self, data):
       
        hhigh = data['high_000905.SH'].iloc[-60:]
        hlow = data['low_000905.SH'].iloc[-60:]
        temp = np.where((hhigh>hhigh.shift(1)) & (hlow>hlow.shift(1)), 4, np.where((hhigh<hhigh.shift(1)) & (hlow<hlow.shift(1)), 0, 1))
        
        return np.nanmean(temp[-45:])