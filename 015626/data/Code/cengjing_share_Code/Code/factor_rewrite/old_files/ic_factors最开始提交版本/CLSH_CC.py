# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 17:55:23 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

    
class CLSH_CC(FutureFactor):

    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'share']}
    normalize_size = 242*3
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = data['close_cont_IC'].iloc[-1001:].values
        temp1 = (np.where(np.diff(hclose)>0, 1, np.where(np.diff(hclose)<0, -1, 0)))
        
        hshare = data['share_cont_IC'].iloc[-1000:].values

        temp2 = np.abs(hshare * temp1)
        hdl_ind_r = bk.move_mean(temp2, 30, min_count = 15, axis = 0)

        factor = rolling_norm(hdl_ind_r, 242*4)
        factor = np.nanmean(factor[-5:])
        return factor