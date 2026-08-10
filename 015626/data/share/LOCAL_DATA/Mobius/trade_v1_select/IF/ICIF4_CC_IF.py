# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:45:05 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class ICIF4_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    
    def calculate(self, data):

        hclose = data['close_000905.SH'].values[-62:]
        temp = np.nanmean(hclose[-60:]) - np.nanmean(shift(hclose, 20)[-40:])
        factor = np.abs(temp)
        return factor