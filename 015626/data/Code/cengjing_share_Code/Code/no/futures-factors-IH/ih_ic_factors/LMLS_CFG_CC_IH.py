# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:01:37 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class LMLS_CFG_CC_IH(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','low', 'adjfactor']
    data_dict['Index_Id'] = {'000016.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        index_close = data['close_000016.SH'].iloc[-1203:]
        stk_close = data['close_preadj'].iloc[-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:, 0])
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr_rank = 2 * stk_index_corr.rank(pct=True) - 1
        
        hlow = data['low_preadj'].iloc[-51:]
        hlow_s = hlow.shift(20).iloc[-30:].values
        hlow = hlow.iloc[-50:].values
        i2 = np.nanmean(hlow, axis = 0) - np.nanmean(hlow_s, axis = 0)
        ii2 = np.nanmean(i2*stk_index_corr_rank.values)

        return ii2