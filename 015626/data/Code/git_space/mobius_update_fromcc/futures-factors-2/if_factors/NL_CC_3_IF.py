# -*- coding: utf-8 -*-
"""
Created on Wed May 25 11:55:12 2022

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk

class NL_CC_3_IF(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 3
    data_dict = dict()
    data_dict['Stock'] = ['open', 'high', 'low', 'close']
    normalize_size = 2400
    normalize_type = 'ts_rank' 

    handle_preadj = False
    
    def calculate(self, data):
        
        n = 26
        hhigh = data['high'].values[-627:]
        hopen = data['open'].values[-627:]
        hlow = data['low'].values[-627:]
        hclose = data['close'].values[-627:]
        
        hh = bk.move_max(hhigh, 26,  axis = 0)[-600:]
        ll = bk.move_min(hopen, 26, axis = 0)[-600:]
        a =  hh- hopen[:-26][-600:]
        b = hclose[-600:] - ll
        c = hh - ll
        vwtc_r = (a+b)/r(c)
        factor = np.nanmean(vwtc_r, axis = 1)
        factor = ts_rank(factor, 600)
        return -(1-abs(factor))[-1]