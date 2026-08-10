# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:09:30 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

    
class HLLSVol_CC(FutureFactor):

    data_type = 'Future'
    days_past = 2
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high','low']} 
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '[0, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        hlow = (data['low_cont_IC'].values)[-250:]
        hhigh = (data['high_cont_IC'].values)[-250:]
        a = bk.move_std(hhigh/hlow, 240, min_count = 10)
        a[a<1e-10] = np.nan
        factor = bk.move_std(hhigh/hlow, 40, min_count = 10)/a
        return factor[-1]
