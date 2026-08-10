# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:03:29 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

    
class CDO_ind_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_000905.SH'].values[-150:]
        hopen = data['open_000905.SH'].values[-150:]
        factor = np.nanmean(hclose)-np.nanmean(hopen)
        
        return factor