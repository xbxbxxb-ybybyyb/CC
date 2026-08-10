# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:49:08 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    
        
class SYXWR_ind_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        hopen = (data['open_000300.SH'].values)[-150:]
        hhigh = (data['high_000300.SH'].values)[-150:]
        hlow = (data['low_000300.SH'].values)[-150:]
        hclose = (data['close_000300.SH'].values)[-150:]
        
        temp1 = np.where(hopen>hclose, hopen, hclose)
        
        a = bk.move_mean((hhigh - temp1), 35, min_count = 15)
        b = bk.move_max(hhigh, 35, min_count = 15) - bk.move_min(hlow, 35, min_count = 15)
        a[abs(a)<1e-8] = np.nan
        b[abs(b) < 1e-8] = np.nan
        t_pcor = (hhigh-temp1)/a
        
        t_pcor2 = (hclose-bk.move_min(hlow, 35, min_count = 15))/b

        return np.nanmean((t_pcor2 - t_pcor)[-60:])