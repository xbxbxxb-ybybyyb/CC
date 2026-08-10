# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:34:11 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class ZHZH_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        hhigh = (data['high_cont_IC'].values)[-110:]
        factor = bk.move_mean((hhigh>=bk.move_max(hhigh, 10, min_count = 5)).astype(int), 90, min_count = 5)
        
        return factor[-1]