# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:09:08 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

    
class HL123_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high','low']} 
    instrument_type='recent'
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '[0, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        hlow = (data['low_cont_IC'].values)[-120:]
        hhigh = (data['high_cont_IC'].values)[-120:]
        i11 = bk.move_max(hhigh, 10, min_count = 5) - bk.move_min(hlow, 60, min_count = 10)
        shift_low = shift(hlow,30)
        shift_high = shift(hhigh, 30)
        shift_low[shift_low==0] = np.nan
        shift_high[shift_high == 0]=np.nan
        i12 = bk.move_max(shift_high, 10, min_count = 5) - bk.move_min(shift_low, 60, min_count = 10)
        #print(bk.move_min(shift_low, 60, min_count = 10)[-1])
        factor = np.nanmean((i11-i12)[-20:])
        return factor

