# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:04:36 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

    
class ClMaxClMin_IFIC_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close']} 
    normalize_size = 3 * 240
    normalize_type = 'ts_rank'
    instrument_type='recent'
    
    def calculate(self, data):
        
        hclose = data['close_cont_IF'].values[-30:]
        
        factor = np.nanmax(hclose)/np.nanmin(hclose)

        
        return factor