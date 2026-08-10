# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:06:35 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class GA_ind_IFIC_CC_IH(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close', 'high', 'low', 'open']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        n = 120
        hclose = (data['close_000016.SH'].values)[-150:]
        hhigh = (data['high_000016.SH'].values)[-150:]
        hlow = (data['low_000016.SH'].values)[-150:]
        hopen = (data['open_000016.SH'].values)[-150:]
        a = np.nanmax(hhigh[-n:])-shift(hopen, n)[-1]
        b = hclose[-1] - np.nanmin(hlow[-n:])
        c = (np.nanmax(hhigh[-n:])-np.nanmin(hlow[-n:]))*2
        if abs(c) < 1e-8:
            c = np.nan 
        factor = (a*b)/c

        return factor