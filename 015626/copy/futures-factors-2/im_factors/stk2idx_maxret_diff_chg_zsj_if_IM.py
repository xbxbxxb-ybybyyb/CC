# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 14:01:37 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class stk2idx_maxret_diff_chg_zsj_if_IM(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'low', 'high']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        stk_close = data['close_preadj'].iloc[-100:]
        stk_close[abs(stk_close) < 1e-8] = np.nan
        stk_ret = stk_close / stk_close.shift(1) - 1

        ret_win = 60
        stk_max_ret = multi_processing_joblib(df=stk_ret, func=get_top_mean, n_jobs=20, d=ret_win)

        # common code for maxret_diff
        ret_win_short = 5
        stk_ret_duration = stk_close/stk_close.shift(ret_win_short) - 1 
        stk_maxret_diff = stk_max_ret - (stk_ret_duration/ret_win_short)
        stk_maxret_diff[~np.isfinite(stk_maxret_diff)] = np.nan
        stk2idx_maxret_diff_raw = np.nanmean(stk_maxret_diff, axis = 1)

        # factor logic
        short_win = 10
        long_win = 35
        min_pct = 0.9
        #stk2idx_maxret_diff_chg = calc_change_helper(stk2idx_maxret_diff_raw,short_win,long_win,ts_pct_win)
        factor = np.nanmean(stk2idx_maxret_diff_raw[-short_win:]) - np.nanmean(stk2idx_maxret_diff_raw[-long_win:])
        
        return factor
    