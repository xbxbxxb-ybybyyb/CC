# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:00:38 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class L123_CC_nr_vs_CFG_CC_IH(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','weight','low', 'high', 'adjfactor']
    normalize_size = 720 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        stk_close = data['close_preadj'].iloc[-73:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        mask = (stk_volatility).values[-40:]
        hlow = data['low_preadj'].iloc[-1400:].values
        i11 = bk.move_min(hlow, 10, min_count = 5, axis = 0) - bk.move_min(hlow, 25, min_count = 10, axis = 0)
        i12 = bk.move_min(hlow, 20, min_count = 15, axis = 0) - bk.move_min(hlow, 30, min_count = 10, axis = 0)
        i2 = (i11-i12)
        
        i_temp = rolling_norm(i2)[-40:]
        
        ii2 = i_temp*mask

        factor = np.nansum(ii2, axis = 1)    
        factor = np.nanmean(factor)
        return factor