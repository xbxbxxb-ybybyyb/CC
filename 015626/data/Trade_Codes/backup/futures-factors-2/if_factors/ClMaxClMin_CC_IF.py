# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:41:09 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

# 先mask再rolling
class ClMaxClMin_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 9
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = '(-0, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_cont_IC'].values[-2000:]
        factor0 = bk.move_max(hclose, 40, min_count = 30)/bk.move_min(hclose, 40, min_count = 30)

        factor1 = rolling_norm(factor0, 242*2)

        factor = bk.move_mean(factor1, 2, min_count = 1)
        
        return factor[-1]