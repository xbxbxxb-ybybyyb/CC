# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 12:08:23 2022

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

    
class XWR_CFG_CC_IF_IM(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'low', 'high','open', 'amount']
    normalize_size = 900
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):

        hopen = data['open'].iloc[-19:].values
        hhigh = data['high'].iloc[-19:].values
        hclose = data['close'].iloc[-19:].values
        hlow = data['low'].iloc[-19:].values

        amount = data['amount'].iloc[-3:]      
        stk_amount_rank = (2 * amount.rank(axis=1, pct=True) - 1)

        temp1 = (np.where(hopen>hclose, hopen, hclose))

        b = bk.move_mean((hhigh - temp1), 15, min_count = 1, axis = 0)
        b[abs(b)<1e-8] = np.nan
        t_pcor = (hhigh - temp1)/b
        h = bk.move_max(hhigh, 15, min_count = 1, axis = 0)
        l = bk.move_min(hlow, 15, min_count = 1, axis = 0)
        a = h-l
        t_pcor2 = (hclose-l)/a
        t_pcorr = (t_pcor2 - t_pcor)[-3:]
        t = np.nansum(t_pcorr * stk_amount_rank, axis = 1)
        factor = np.nanmean(t[-3:])

        return factor
