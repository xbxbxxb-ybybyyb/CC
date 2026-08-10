# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:08:12 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class HcorrC_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':[ 'high', 'close']}
    normalize_size = 2420
    normalize_type = 'ts_rank'
    #num_range = [0.0001, 1]
    
    def calculate(self, data):

        high = data['high_000905.SH'].iloc[-60:]
        close = data['close_000905.SH'].iloc[-60:]
        factor = high.corr(close)
        return factor