# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:05:48 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
  

class CloseVoltoMean_IFIC_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = [-0.2, 1]
    
    def calculate(self, data):
        
        hclose = (data['close_000300.SH'].values)[-41:]
        return np.nanmean((bk.move_std(hclose, 30, min_count = 10, axis = 0)/bk.move_mean(hclose, 30, min_count = 15, axis = 0))[-10:])

