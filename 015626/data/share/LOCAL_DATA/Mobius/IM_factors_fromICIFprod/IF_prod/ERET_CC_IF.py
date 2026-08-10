# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 13:09:00 2022

@author: appadmin
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 18:31:06 2021

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk

    
class ERET_CC_IF(FutureFactor):
    
    data_type = 'Future' 
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close', 'volume']}

    normalize_size = 200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        # aa = 2, bb = 10, ccc = 30
        index_close = data['close_000300.SH'].values[-42:]
        index_volume = data['volume_000300.SH'].values[-41:]
        ret = index_close[1:]/index_close[:-1] - 1

        ret_std = bk.move_std(ret, 10, 1, axis = 0)
        ret_weight = ret * ret_std / index_volume
        factor = np.nanmean(ret_weight[-30:])
        return factor
