# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:53:57 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



class HHLS_ar_CC_CFG_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','high','amount']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        stk_amount = (data['amount']).iloc[-5:]
        stk_amount_rank = 2 * stk_amount.rank(axis=1, pct=True) - 1
        mask = stk_amount_rank.values
        
        hhigh = data['high_preadj'].iloc[-56:].values
        hhigh_s = data['high_preadj'].iloc[-200:].shift(50).values[-56:]
        
        temp = (bk.move_max(hhigh, 50, min_count = 15, axis = 0) - bk.move_max(hhigh_s, 50, min_count = 15, axis = 0))[-5:]
        tempdf = np.nansum(temp*mask, axis = 1)

        factor = np.nanmean(tempdf)
        
        return factor