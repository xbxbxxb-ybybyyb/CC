# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:40:48 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    
class CPLR_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 242*2
    normalize_type = 'ts_rank'
    #num_range = '(-0, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_000300.SH'].values[-116:]
        temp = bk.move_max(hclose, 40, min_count = 20)
        x = np.array(range(len(temp)))
        factor = rolling_linear_reg(x, temp, 75)
        
        return factor[-1]
