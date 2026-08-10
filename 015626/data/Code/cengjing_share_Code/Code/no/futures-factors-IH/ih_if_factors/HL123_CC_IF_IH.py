# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:42:51 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

class HL123_CC_IF_IH(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':['close', 'high', 'low', 'open']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        
        hhigh = (data['high_cont_IH'].values)[-120:]
        hlow = (data['low_cont_IH'].values)[-120:]
        
        i11 = bk.move_max(hhigh, 10, min_count = 5) - bk.move_min(hlow, 60, min_count = 10)
        shift_low = shift(hlow,30)
        shift_high = shift(hhigh, 30)
        shift_low[shift_low==0] = np.nan
        shift_high[shift_high == 0]=np.nan
        i12 = bk.move_max(shift_high, 10, min_count = 5) - bk.move_min(shift_low, 60, min_count = 10)
        #print(bk.move_min(shift_low, 60, min_count = 10)[-1])
        factor = np.nanmean((i11-i12)[-20:])

        return factor
    