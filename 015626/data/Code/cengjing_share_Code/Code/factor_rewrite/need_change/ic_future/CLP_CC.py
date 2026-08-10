# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:23:48 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

# 先mask后rolling
class CLP_CC(FutureFactor):

    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close','OpenInterest']}  
    normalize_size = 1200
    normalize_type = 'rolling_norm'
    num_range = '[-0.3, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        
        hclose = (data['close_cont_IC'].values)[-30:]
        hclose = np.sign(hclose)
        position = (data['OpenInterest_cont_IC'].values)[-31:]

        temp3 = position[1:] - position[:-1]
        temp2 = np.abs(temp3*hclose)
        
        factor = np.nanmean(temp2)

        return factor