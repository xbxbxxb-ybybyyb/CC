# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:49:25 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    

class VMaxVmean_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['vwap']} 
    #data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']}
    normalize_size = 480
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        vwap = (data['vwap_cont_IC'].values)[-61:]
        factor = np.nanmax(vwap[-60:])/np.nanmin(vwap[-60:])

        return factor