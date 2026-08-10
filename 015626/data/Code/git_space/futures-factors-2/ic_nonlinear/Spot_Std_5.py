# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 13:27:39 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class Spot_Std_5(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']} 
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        
        hclose = data['close_000905.SH'].iloc[-6:].values
        
        factor = np.nanstd(hclose[1:] / hclose[:-1] - 1)

        
        return factor