# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 10:13:32 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from operators_cc import *
import pandas as pd

class CloseVoltoMean_cr_CFG_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'volume', 'close', 'adjfactor', 'stk_index_corr_zz500']
    #data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 720 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        stk_index_corr = data['stk_index_corr_zz500'].iloc[-61:]
        
        mask = (2 * stk_index_corr.rank(axis=1, pct=True) - 1).values
        
        stk_close = data['close_preadj'].iloc[-61:]
        
        prstd3_r = bk.move_std(stk_close, 40, min_count = 5, axis = 0)/bk.move_mean(stk_close, 40, min_count = 5, axis = 0)
        
        factor = np.nansum((prstd3_r*mask), axis = 1)
        factor = np.nanmean(factor[-20:])

        return factor