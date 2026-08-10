# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:42:29 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class HHLS_ind_ICIF_CC_IF_IH(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close', 'high', 'low', 'open']} 
    normalize_size = 5 * 240
    normalize_type = 'rolling_norm'
    #num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        
        hhigh = (data['high_000016.SH'].values)[-120:]
        factor = np.nanmax(hhigh[-50:]) - np.nanmax(shift(hhigh, 50)[-50:])

        return factor