# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:25:42 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class LSC_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 5
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high','close', 'low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '[0, 1]'
    instrument_type='recent'
    
    def calculate(self, data):

        high = (data['high_cont_IC'].values)[-1100:]
        close = (data['close_cont_IC'].values)[-1100:]
        low = (data['low_cont_IC'].values)[-1100:]
        temp = (bk.move_max(high, 30, min_count = 10)- bk.move_min(low, 30, min_count = 10))
        temp[abs(temp)<0.0001] = np.nan
        hh = (bk.move_max(high, 30, min_count = 10) - close)/temp
        ll = (close -bk.move_min(low, 30, min_count = 10))/temp
        factor = bk.move_mean(ll, 20, min_count =15) - bk.move_mean(hh, 20, min_count =15)
        factor = rolling_norm(factor, 242*4)
        factor[factor<=-0.5] = np.nan
        factor = bk.move_mean(factor, 3, min_count = 2)
        return factor[-1]
    