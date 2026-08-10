# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:33:27 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class SYXWR_ind_CC_IH(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':[ 'high', 'low', 'close', 'open']}
    instrument_type='recent'
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [-1, 1]
    
    def calculate(self, data):
        hopen = (data['open_000016.SH'].values)[-120:]
        hhigh = (data['high_000016.SH'].values)[-120:]
        hlow = (data['low_000016.SH'].values)[-120:]
        hclose = (data['close_000016.SH'].values)[-120:]
        
        temp1 = np.where(hopen>hclose, hopen, hclose)
        #temp2 = np.where(hopen>hclose, hclose, hopen)
        
        b = bk.move_mean((hhigh - temp1), 30, min_count = 15)
        b[abs(b)<1e-8] = np.nan
        t_pcor = (hhigh-temp1)/b
        a = bk.move_max(hhigh, 30, min_count = 15) - bk.move_min(hlow, 30, min_count = 15)
        a[abs(a) < 1e-8] = np.nan
        t_pcor2 = (hclose-bk.move_min(hlow, 30, min_count = 15))/a

        
        return np.nanmean((t_pcor2 - t_pcor)[-90:])