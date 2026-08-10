# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:44:49 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

# 先mask再rolling
class ICIF1_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = '[-0, 1]'
    
    def calculate(self, data):

        hclose = data['close_cont_IC'].iloc[-1230:]
        temp5 = bk.move_mean(hclose, 5, min_count = 2)
        temp10 = bk.move_mean(hclose, 10, min_count = 5)
        temp20 = bk.move_mean(hclose, 20, min_count = 10)
        temp60 = bk.move_mean(hclose, 60, min_count = 30)
        temp120 = bk.move_mean(hclose, 120, min_count = 60)
        
        temp5_diff = (np.diff(temp5)>0).astype(int)
        temp10_diff = (np.diff(temp10)>0).astype(int)
        temp20_diff = (np.diff(temp20)>0).astype(int)
        temp60_diff = (np.diff(temp60)>0).astype(int)
        temp120_diff = (np.diff(temp120)>0).astype(int)
        factor = ts_rank(bk.move_mean(temp5_diff+temp10_diff+temp20_diff+temp60_diff+temp120_diff, 15, min_count = 5))
        factor = np.nanmean(factor[-10:])
        return factor
    
    
