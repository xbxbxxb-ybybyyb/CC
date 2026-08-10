# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:24:26 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class L123_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':[ 'low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [0.0001, 1]
    
    def calculate(self, data):

        hlow = (data['low_000905.SH'].values)[-80:]
        i11 = bk.move_min(hlow, 10, min_count = 5) - bk.move_min(hlow, 25, min_count = 10)
        i12 = bk.move_min(hlow, 20, min_count = 15) - bk.move_min(hlow, 30, min_count = 10)
        i2 = bk.move_mean((i11-i12), 25, min_count = 2)

        
        return i2[-1]