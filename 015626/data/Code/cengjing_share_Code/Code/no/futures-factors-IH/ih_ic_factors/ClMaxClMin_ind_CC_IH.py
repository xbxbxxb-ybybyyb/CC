# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:05:21 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
  
class ClMaxClMin_ind_CC_IH(FutureFactor):

    data_type = 'Future'
    days_past = 1
    instrument_type='recent'
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    num_range = None
    instrument_type='recent'
    
    def calculate(self, data):
        
        hclose = data['close_000016.SH'].values[-60:]
        
        factor = np.nanmax(hclose)/np.nanmin(hclose)
        
        return factor
