# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:09:24 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class HDL_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high', 'low']} 
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        
        hhigh = data['high_cont_IC'].iloc[-50:]
        hlow = data['low_cont_IC'].iloc[-50:]
        hdl_r = (bk.move_max(hhigh, 25, min_count = 10, axis = 0))/(bk.move_min(hlow, 25, min_count = 10, axis = 0))
        factor = np.nanmean(hdl_r[-10:])
        
        return factor