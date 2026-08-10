# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:59:38 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    
class td_cv_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'stk_index_corr_hs300', 'low', 'high']
    normalize_size = 720 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        stk_close = data['close_preadj'].iloc[-50:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30).iloc[-15:]
        stk_index_corr = data['stk_index_corr_hs300'].iloc[-15:]
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        temp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0) 
        mask = temp2 * temp3

        hhigh = data['high_preadj'].iloc[-77:].values
        hlow = data['low_preadj'].iloc[-77:].values
        
        temp = bk.move_min(hlow, 10, min_count = 5, axis = 0)-bk.move_min(hlow, 60, min_count = 5, axis = 0)+bk.move_max(hhigh, 10, min_count = 5, axis = 0)-bk.move_max(hhigh, 60, min_count = 5, axis = 0)
        temp = temp[-15:]
        tempdf = np.nanmean(temp*mask, axis = 1)
        factor = np.nanmean(tempdf)
        
        return factor