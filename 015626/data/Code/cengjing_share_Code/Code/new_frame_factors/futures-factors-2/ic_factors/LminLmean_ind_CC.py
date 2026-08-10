# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:30:37 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class LminLmean_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':[ 'low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [-0.499999, 1]
    
    def calculate(self, data):


        low = data['low_000905.SH'].values[-50:]
        temp1 = np.nanmin(low)
        temp2 = np.nanmean(low[-30:])
        factor = -temp1/temp2
        return factor