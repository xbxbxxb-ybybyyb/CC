# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:48:15 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



class RolTrendLS_ind_CC_IF_IH(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000016.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = '[-0.5, 1]'
    
    def calculate(self, data):
        hclose = (data['close_000016.SH'].values)[-100:]
        hhigh = (data['high_000016.SH'].values)[-100:]
        hlow = (data['low_000016.SH'].values)[-100:]
        temp = (bk.move_max(hhigh, 60, min_count = 15) - bk.move_min(hlow, 60, min_count = 15))
        temp[abs(temp)<0.00001] = np.nan
        ll = (hclose-bk.move_min(hlow, 60, min_count = 15)) / temp
        a2 = bk.move_mean(ll, 10, min_count = 5)
        a3 = bk.move_mean(a2, 10, min_count = 5)
        vwtc_r = 3*a3-2*a2
        
        return np.nanmean(vwtc_r[-5:])