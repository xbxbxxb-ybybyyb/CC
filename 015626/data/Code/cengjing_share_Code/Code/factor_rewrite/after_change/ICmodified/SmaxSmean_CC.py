# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:33:48 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class SmaxSmean_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['share']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        hshare = (data['share_cont_IC'].values)[-120:]
        
        a = np.nanmean(hshare[-30:])
        b = np.nanmean(hshare)
        factor = a-b
        return factor
