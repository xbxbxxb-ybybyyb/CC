# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:45:54 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


    
class LCCorr_ind_ICIF_CC_IF_IH(FutureFactor):
    
    data_type = 'Future'
    days_past = 12
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000016.SH':['close', 'low']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    #num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        high = data['low_000016.SH'].iloc[-1300:]
        close = data['close_000016.SH'].iloc[-1300:]
        temp = high.rolling(60, min_periods = 30).corr(close)
        temp[abs(temp)>100] = np.nan
        factor = bk.move_mean(temp, 5, min_count = 2)

        factor = rolling_norm(factor, method = 'ts_rank')
        return factor[-1]
    