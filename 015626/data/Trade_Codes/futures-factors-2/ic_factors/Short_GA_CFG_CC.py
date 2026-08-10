# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 14:25:07 2021

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class Short_GA_CFG_CC(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor','open','high','low', 'amount']

    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        df_s = np.nansum(data['amount'].values[-120:], axis = 0)

        amount_mask = np.nanquantile(df_s, 0.9)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        
        high = data['high_preadj'].values[-35:]
        close = data['close_preadj'].values[-35:]
        opendf = data['open_preadj'].values[-36:]
        low = data['low_preadj'].values[-35:]
        t1 = np.nanmax(high, axis = 0)
        t2 = np.nanmin(low, axis = 0)
        a = t1 - opendf[0]
        b = close[-1] - t2
        c = (t1-t2)*2
        factor_raw = (a+b)/r(c)

        factor_raw_after_mask = ma.array(factor_raw, mask=(df_s<=amount_mask))
        factor = np.nanmean(factor_raw_after_mask)
        
        return factor
    
