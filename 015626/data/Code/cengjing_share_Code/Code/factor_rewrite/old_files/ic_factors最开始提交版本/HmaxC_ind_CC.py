# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:22:30 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


    
class HmaxC_ind_CC(FutureFactor):
  
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high', 'low', 'close']}
    normalize_size = 1000
    normalize_type = 'ts_rank'
    num_range = '[0, 1]'
    
    def calculate(self, data):

        hhigh = (data['high_000905.SH'].values)[-130:]
        hclose =(data['close_000905.SH'].values)[-130:]
        temp1 = -bk.move_max(hhigh, 120, min_count = 90) / hclose
        temp1[abs(temp1)>100000] = np.nan
        
        return temp1[-1]  