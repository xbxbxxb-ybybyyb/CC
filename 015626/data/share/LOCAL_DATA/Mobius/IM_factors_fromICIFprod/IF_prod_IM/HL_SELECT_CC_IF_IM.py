# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 18:54:48 2022

@author: appadmin
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 19:12:22 2021

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk


class HL_SELECT_CC_IF_IM(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'high', 'low', 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        hclose = data['close'].values[-16:]
        hret = hclose[1:]/hclose[:-1] - 1

        df_s = np.nanmax(data['high'].values[-50:], axis = 0)/ (np.nanmin(data['low'].values[-50:], axis = 0))       
        hret = np.nanmean(hret, axis = 0) * data['weight'].values[-1]
        try:
            df_s_mask = np.nanmedian(df_s)
            df_s_mask = np.expand_dims(df_s_mask, axis = -1)
            hret_1 = ma.array(hret, mask=(df_s<=df_s_mask))
            hret_2 = ma.array(hret, mask=(df_s>=df_s_mask))
            temp2 = np.nanmean(hret_1) - np.nanmean(hret_2)
        except:
            temp2 = np.nan
        return temp2