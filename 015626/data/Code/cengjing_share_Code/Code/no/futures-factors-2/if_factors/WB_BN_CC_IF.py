# -*- coding: utf-8 -*-
"""
Created on Sun May 15 18:21:37 2022

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

def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))

class WB_BN_CC_IF(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 3
    data_dict = dict()
    data_dict['Stock'] = ['WeightSellOrderQtySumMean', 'WeightBuyOrderQtySumMean','BuyUniqueOrderNum','BuyTradeNum','weight']
    normalize_size = 2400
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        m = data['BuyUniqueOrderNum'].iloc[-120:]
        bn = (data['BuyUniqueOrderNum'].values[-600:]/ r(data['BuyTradeNum'].values[-600:])) 
        
        temp1 = bk.move_max(bn, 480, min_count = 1, axis = 0)[-120:]        
        temp2 = bk.move_min(bn, 480, min_count = 1, axis = 0)[-120:]        
        temp3 = r(temp1 - temp2)   
        
        factor1 = (bn[-120:] - temp2)/temp3        
        factor2 = (temp1 - bn[-120:])/temp3
        weight = data['weight'].values[-120:]
        factor_raw = ((factor1 - factor2) * weight)
             
        df_s = (data['WeightBuyOrderQtySumMean'] / r(data['WeightSellOrderQtySumMean']))
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        
        factor_raw = pd.DataFrame(factor_raw, index = m.index, columns = m.columns)
        
        factor = (factor_raw[bool_df]).ewm(span = 2, min_periods = 1).mean().values
        
        
        return -np.nanmean(factor[-1])
        #factor_raw = (ts_truncated_ema_span_1(factor_raw, 20, 2))
        #return np.nanmean(factor_raw[-1])