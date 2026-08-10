# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:33:09 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class RolTrendLS_ind_CC_IH(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':[ 'high', 'low', 'close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [-1, 1]
    
    def calculate(self, data):
        hclose = (data['close_000016.SH'].values)[-85:]
        hhigh = (data['high_000016.SH'].values)[-85:]
        hlow = (data['low_000016.SH'].values)[-85:]
        a = bk.move_max(hhigh, 60, min_count = 15) - bk.move_min(hlow, 60, min_count = 15)
        a[abs(a)<1e-8] = np.nan
        ll = (hclose - bk.move_min(hlow, 60, min_count = 15))/a
        a2 = bk.move_mean(ll, 10, min_count = 5)
        a3 = bk.move_mean(a2, 10, min_count = 5)
        vwtc_r = 3*a3-2*a2
        return vwtc_r[-1]
    