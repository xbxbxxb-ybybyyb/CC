# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 19:36:42 2021

@author: appadmin
"""
import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk

class ABS_DIS_CC_IF_IH(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'weight']
    normalize_size = 210
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):

        df_s = data['weight'].values[-1]
        hclose = data['close'].values[-35:]
        pchange = (hclose[30:] - hclose[:-30])[-1]
        temp = np.nanmean(abs(hclose[1:] - hclose[:-1])[-30:], axis = 0)
        amount_mask = np.nanquantile(df_s, 0.75)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        factor_raw = pchange/r(temp)
        
        factor_raw_after_mask = ma.array(factor_raw, mask=(df_s<=amount_mask))
        factor_raw_after_mask = np.nanmean(factor_raw_after_mask)
        
        return factor_raw_after_mask 