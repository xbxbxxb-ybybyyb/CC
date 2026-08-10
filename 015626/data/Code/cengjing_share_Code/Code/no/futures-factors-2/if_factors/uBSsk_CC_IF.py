# -*- coding: utf-8 -*-
"""
Created on Sun May 15 18:48:37 2022

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
from scipy.stats import skew


class uBSsk_CC_IF(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum','BuyTradeNum','SellUniqueOrderNum','SellTradeNum']
    normalize_size = 200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        m = data['BuyUniqueOrderNum'].iloc[-3:]
        factor1 = (data['BuyUniqueOrderNum'].values[-3:] / r(data['BuyTradeNum']).values[-3:]) 
        factor2 = (data['SellUniqueOrderNum'].values[-3:]  / r(data['SellTradeNum']).values[-3:])
        factor1 = pd.DataFrame(factor1, index = m.index, columns = m.columns)
        factor2 = pd.DataFrame(factor2, index = m.index, columns = m.columns)
        factor = 11*(factor1).skew(axis = 1) - 9*factor2.skew(axis = 1)
        factor = np.nanmean(factor)
        
        
        return factor
        #factor_raw = (ts_truncated_ema_span_1(factor_raw, 20, 2))
        #return np.nanmean(factor_raw[-1])