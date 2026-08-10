# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:34:38 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class ZHZH_ind_CC_IH(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['high']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '[0, 1]'
    
    def calculate(self, data):
        hhigh = (data['high_000016.SH'].values)[-80:]
        factor = bk.move_mean((hhigh>=bk.move_max(hhigh, 15, min_count = 5)).astype(int), 60, min_count = 5)
        
        return factor[-1]
