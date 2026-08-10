# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:22:08 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class HLTM_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high', 'low', 'close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [0, 1]
    
    def calculate(self, data):
        hlow = (data['low_000905.SH'].values)[-1100:]
        hhigh = (data['high_000905.SH'].values)[-1100:]
        hclose =(data['close_000905.SH'].values)[-1100:]
        temp1 = bk.move_max(hhigh, 15, min_count = 7) - hclose
        temp2 = hclose - bk.move_min(hlow, 15, min_count = 7)
        temp = np.where(temp1>temp2, temp1, temp2)
        factor0 = bk.move_mean(temp, 30, min_count = 15)
        factor = rolling_norm(factor0, 242*4)
        return factor[-1]