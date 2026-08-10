# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:03:20 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


#
class SYXWR_ar_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'low', 'high','open', 'amount', 'adjfactor']
    normalize_size = 2400 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hopen = data['open_preadj'].iloc[-85:].values
        hhigh = data['high_preadj'].iloc[-85:].values
        hclose = data['close_preadj'].iloc[-85:].values
        hlow = data['low_preadj'].iloc[-85:].values
        
        amount = data['amount'].iloc[-50:]      
        stk_amount_rank = (2 * amount.rank(axis=1, pct=True) - 1)
        
        temp1 = (np.where(hopen>hclose, hopen, hclose))
        
        b = bk.move_mean((hhigh - temp1), 30, min_count = 15, axis = 0)
        b[abs(b)<1e-8] = np.nan
        t_pcor = (hhigh - temp1)/b
        h = bk.move_max(hhigh, 30, min_count = 15, axis = 0)
        l = bk.move_min(hlow, 30, min_count = 15, axis = 0)
        a = h-l
        t_pcor2 = (hclose-l)/a
        t_pcorr = (t_pcor2 - t_pcor)[-50:]
        t = np.nansum(t_pcorr * stk_amount_rank, axis = 1)
        factor = bk.move_sum(t, 40, min_count = 20, axis = 0)
        factor = factor[-1]
        
        return factor