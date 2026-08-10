# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:41:33 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *
      
class CloseVoltoMean_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_000905.SH'].values[-50:]
        factor0 = bk.move_std(hclose, 30, min_count = 15)/bk.move_mean(hclose, 30, min_count = 15)

        factor = np.nanmean(factor0[-15:])
   
        return factor