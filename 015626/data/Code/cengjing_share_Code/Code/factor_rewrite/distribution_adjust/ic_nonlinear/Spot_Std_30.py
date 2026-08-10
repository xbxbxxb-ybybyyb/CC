# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 15:46:46 2022

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class Spot_Std_30(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']} 
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        
        hclose = data['close_000905.SH'].iloc[-31:].values
        
        factor = np.nanstd(hclose[1:] / hclose[:-1] - 1)

        return np.log(factor) if factor > 0 else np.nan