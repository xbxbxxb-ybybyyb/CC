# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:09:05 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class ClMaxClMin_CC_IH(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':['close']} 
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    instrument_type='recent'
    
    def calculate(self, data):
        hclose = data['close_cont_IH'].iloc[-45:].values
        
        return np.nanmax(hclose)/np.nanmin(hclose)