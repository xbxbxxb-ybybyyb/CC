# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:34:59 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class fvs2_ind_IFIC_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    data_dict['Continuous_Data'] = {'IF':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    instrument_type='recent'
   # num_range = [0, 1]
    
    def calculate(self, data):
        close_spot = (data['close_000300.SH']).iloc[-52:]
        close = (data['close_cont_IF']).iloc[-52:]
        vwtc_r = close.rolling(40, min_periods=15).corr(close_spot)
        vwtc_r  = vwtc_r.replace([-np.inf, np.inf], np.nan)
        vwtc_r = vwtc_r.values
        factor = (vwtc_r*(np.sign(-(close-close_spot))))
        factor = np.abs(factor)
        factor = bk.move_mean(factor, 5, min_count = 2)
        
        return factor[-1]
    