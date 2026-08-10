# -*- coding: utf-8 -*-
"""
Created on Wed May 25 14:45:26 2022

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk

class NL_CC_4_IF_IM(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['open', 'high', 'low', 'close', 'amount']
    normalize_size = 1200
    normalize_type = 'ts_rank' 

    handle_preadj = False
    
    def calculate(self, data):
        
        stk_amount = (data['amount']).values[-2:]
        bool_df = section_rank_np(stk_amount, pct=True) * 2 - 1
        hhigh = data['high'].values[-28:]
        hopen = data['open'].values[-28:]
        hlow = data['low'].values[-28:]
        hclose = data['close'].values[-28:]
        
        hh = bk.move_max(hhigh, 25,  axis = 0)[-2:]
        ll = bk.move_min(hlow, 25, axis = 0)[-2:]
        a =  hh - hopen[:-25][-2:]
        b = hclose[-2:] - ll
        c = hh - ll
        vwtc_r = (a+b)/r(c)
        factor = np.nanmean(vwtc_r * bool_df, axis = 1)
        factor = np.nanmean(factor)

        return factor
