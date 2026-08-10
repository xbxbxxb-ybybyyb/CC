# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 13:42:04 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class Spot_mom_30_im(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000852.SH':['close']} 
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        
        hclose = data['close_000852.SH'].iloc[-31:].values
        
        factor = (hclose[-1] / hclose[1] - 1)

        
        return factor