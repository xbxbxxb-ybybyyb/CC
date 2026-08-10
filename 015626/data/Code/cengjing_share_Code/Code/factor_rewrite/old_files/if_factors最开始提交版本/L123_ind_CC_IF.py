# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:45:39 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class L123_ind_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000300.SH':['low']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    #num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        hlow = (data['low_000300.SH'].values)[-90:]
        i11 = bk.move_min(hlow, 10, min_count = 5) - bk.move_min(hlow, 25, min_count = 10)
        i12 = bk.move_min(hlow, 20, min_count = 15) - bk.move_min(hlow, 30, min_count = 10)
        i2 = np.nanmean((i11-i12)[-60:])
        return i2
    