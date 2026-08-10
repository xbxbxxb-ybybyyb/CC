# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:35:19 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class td_CC_IM(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Index_Id'] = {'000852.SH':['close']}
    data_dict['Index_Id'] = {'000852.SH':['low', 'high']}
    normalize_size = 1200
    normalize_type = 'rolling_norm'
#    num_range = '[-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        hlow = (data['low_000852.SH'].values)[-60:]
        hhigh = (data['high_000852.SH'].values)[-60:]
        templ = np.nanmin(hlow[-10:]) - np.nanmin(hlow)
        temph = np.nanmax(hhigh[-10:]) - np.nanmax(hhigh)
        factor = templ+temph
        return factor