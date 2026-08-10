# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:25:11 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class LCCorr_ind_IFIC_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':[ 'low', 'close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [0.0001, 1]
    
    def calculate(self, data):

        high = data['low_000300.SH'].iloc[-60:]
        close = data['close_000300.SH'].iloc[-60:]
        factor = high.corr(close)
        return factor
    