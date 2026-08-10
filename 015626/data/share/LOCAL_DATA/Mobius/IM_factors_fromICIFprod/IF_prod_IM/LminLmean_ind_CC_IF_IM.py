# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:47:27 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



class LminLmean_ind_CC_IF_IM(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Index_Id'] = {'000852.SH':['low']} 
    data_dict['Index_Id'] = {'000852.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = '[-0.8, 1]'
    
    def calculate(self, data):
        
        low = data['low_000852.SH'].values[-45:]
        
        return -np.nanmin(low)/np.nanmean(low[-25:])