# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:44:27 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

class HcorrC_ind_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    #num_range = '[-0, 1]'
    
    def calculate(self, data):

        high = data['high_000905.SH'].iloc[-120:]
        close = data['close_000905.SH'].iloc[-120:]
        factor = high.rolling(45, min_periods = 30).corr(close)
        factor[abs(factor>10)] = np.nan
        factor = np.nanmean(factor.iloc[-30:])
        return factor
    
