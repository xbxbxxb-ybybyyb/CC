# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:46:52 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class LminC_ind_CC_IF_IH(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['vwap']} 
    data_dict['Index_Id'] = {'000016.SH':['close', 'low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '[-0.8, 1]'
    
    def calculate(self, data):
        
        low = data['low_000016.SH'].values[-180:]
        
        return -np.nanmin(low)/(data['close_000016.SH'].values[-1])
