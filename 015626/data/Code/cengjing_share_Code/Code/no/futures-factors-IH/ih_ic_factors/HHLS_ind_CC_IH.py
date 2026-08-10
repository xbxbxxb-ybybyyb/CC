# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:08:39 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

    
class HHLS_ind_CC_IH(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['high']}  
    normalize_size = 1200
    normalize_type = 'rolling_norm'
    #num_range = [-0.3, 1]
    
    def calculate(self, data):
        
        hhigh = (data['high_000016.SH'].values)[-120:]
        factor = np.nanmax(hhigh[-50:]) - np.nanmax(shift(hhigh, 50)[-50:])

        return factor   
