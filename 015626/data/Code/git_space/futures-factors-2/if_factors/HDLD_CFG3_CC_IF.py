# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 15:11:26 2021

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk

class HDLD_CFG3_CC_IF(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['open','high', 'low', 'close', 'weight']
    normalize_size = 240 *2
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        df_s = data['weight'].values[-65:]
        amount_mask = np.nanquantile(df_s, 0.8, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        hopen = data['open'].values[-65:]
        hclose =data['close'].values[-65:]
        hhigh = data['high'].values[-65:]
        hlow = data['low'].values[-65:]
        
        temp1 = hopen - hclose
        temp2 = hhigh - hlow
        t_pcor2 = -temp1/r(temp2)
        t_pcor2[abs(t_pcor2)>10000] = np.nan
        factor_raw = bk.move_mean(t_pcor2, 60, 2, axis = 0)
        
        factor_raw_after_mask = ma.array(factor_raw, mask=(df_s<=amount_mask))
        factor_raw_after_mask = np.nanmean(factor_raw_after_mask, axis=1)

        return factor_raw_after_mask[-1]