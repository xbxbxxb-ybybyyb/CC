# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:54:50 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class DJC_cv_CFG_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = [  'close', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        index_close = data['close_000905.SH'].iloc[-1206:]
        stk_close = data['close_preadj'].iloc[-1206:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = (stk_ret.rolling(1200, min_periods=1200).corr(index_ret.iloc[:,0])).iloc[-5:]
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        
        stk_volatility = ts_std(stk_ret.iloc[-37:], 30).iloc[-5:]
        tempp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0)
        tempp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        
        hclose = stk_close.iloc[-290:]
        temp5 = bk.move_mean(hclose.iloc[-40:], 5, min_count = 2, axis = 0)
        temp10 = bk.move_mean(hclose.iloc[-40:], 10, min_count = 5, axis = 0)
        temp20 = bk.move_mean(hclose.iloc[-55:], 20, min_count = 10, axis = 0)
        temp60 = bk.move_mean(hclose.iloc[-105:], 60, min_count = 20, axis = 0)
        temp120 = bk.move_mean(hclose.iloc[-205:], 120, min_count = 60, axis = 0)
        
        temp5_diff = ((temp5[1:]-temp5[:-1]>1e-8).astype(int))[-26:]
        temp10_diff = ((temp10[1:]-temp10[:-1]>1e-8).astype(int))[-26:]
        temp20_diff = ((temp20[1:]-temp20[:-1]>1e-8).astype(int))[-26:]
        temp60_diff = ((temp60[1:]-temp60[:-1]>1e-8).astype(int))[-26:]
        temp120_diff = ((temp120[1:]-temp120[:-1]>1e-8).astype(int))[-26:]
        
        temp = (bk.move_mean((temp5_diff+temp10_diff+temp20_diff+temp60_diff+temp120_diff), 20, min_count = 15, axis = 0))[-5:]
        mask = (tempp2 * tempp3).values
        factor = np.nansum((temp*mask), axis = 1)
        factor = np.nanmean(factor)
        
        return factor
