# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:47:58 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



class RolTrendLS_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = '[-0.5, 1]'
    
    def calculate(self, data):
        hclose = (data['close_cont_IF'].values)[-150:]
        hhigh = (data['high_cont_IF'].values)[-150:]
        hlow = (data['low_cont_IF'].values)[-150:]

        ll = hclose-bk.move_min(hlow, 120, min_count = 15) - (bk.move_max(hhigh, 120, min_count = 15) - bk.move_min(hlow, 60, min_count = 15))
        a2 = bk.move_mean(ll, 10, min_count = 5)
        a3 = np.nanmean(a2[-10:])
        vwtc_r = 3*a3-2*a2[-1]
        return vwtc_r