# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:01:01 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class L123_CFG2_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','amount','low', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        amount = data['amount'].iloc[-120:]
        df_s = amount.sum(axis = 0)
        stk_amount = df_s.gt(df_s.quantile(0.90))
        
        index_close = data['close_000905.SH'].iloc[-1203:]
        stk_close = data['close_preadj'].iloc[-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:, 0])
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        mask = (stk_index_corr*stk_amount).values
        
        hlow = data['low_preadj'].iloc[-55:].values
        i11 = bk.move_min(hlow, 10, min_count = 5, axis = 0) - bk.move_min(hlow, 25, min_count = 10, axis = 0)
        i12 = bk.move_min(hlow, 20, min_count = 15, axis = 0) - bk.move_min(hlow, 30, min_count = 10, axis = 0)
        i2 = np.nanmean((i11-i12)[-25:], axis = 0)
    
        ii2 = i2*mask

        factor = np.nanmean(ii2)
        
        return factor