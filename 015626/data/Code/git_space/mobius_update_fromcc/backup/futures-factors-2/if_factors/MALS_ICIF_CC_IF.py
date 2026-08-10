# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:47:43 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    
class MALS_ICIF_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['low']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 242*2
    normalize_type = 'ts_rank'
#    num_range = '[-0.5, 1]'
    
    def calculate(self, data):
        
        low = data['low_000905.SH'].values[-75:]
        factor = bk.move_mean(low, 75, min_count = 15) - bk.move_mean(shift(low, 15), 60, min_count = 7)
        
        return factor[-1]