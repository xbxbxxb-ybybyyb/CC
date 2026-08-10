# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:06:12 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class CloseVoltoMean_ind_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
#    num_range = '(-0.2, 1]'
    
    def calculate(self, data):
        
        hclose = (data['close_000905.SH'].values)[-40:]
        return np.nanstd(hclose)/np.nanmean(hclose)


