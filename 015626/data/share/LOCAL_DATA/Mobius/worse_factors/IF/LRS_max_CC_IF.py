# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:46:29 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

class LRS_max_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['vwap']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 500
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        vwap = data['vwap_cont_IC'].values[-150:]
        temp1 = bk.move_max(vwap, 50, min_count = 20)
        x = np.array(range(len(vwap)))
        factor = (rolling_linear_reg(x, temp1, 50))
        return factor[-1]