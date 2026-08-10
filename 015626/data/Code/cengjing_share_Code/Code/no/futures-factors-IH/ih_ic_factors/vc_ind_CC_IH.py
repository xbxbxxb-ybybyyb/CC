# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:35:38 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class vc_ind_CC_IH(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['volume', 'close']}
    #data_dict['Continuous_Data'] = {'IC':['low', 'high']}
    normalize_size = 1200
    normalize_type = 'rolling_norm'
#    num_range = '[-1, 1]'
    
    def calculate(self, data):
        hvolume = (data['volume_000016.SH'].values)[-20:]
        hclose = (data['close_000016.SH'].values)[-20:]
        factor = bk.move_mean((hvolume-shift(hvolume, 1)), 15, min_count = 7)*(hclose - shift(hclose, 15))
        return -factor[-1]
    
