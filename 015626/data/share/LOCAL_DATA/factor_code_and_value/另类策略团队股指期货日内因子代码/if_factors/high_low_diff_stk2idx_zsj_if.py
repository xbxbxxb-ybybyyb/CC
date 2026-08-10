# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:59:59 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class high_low_diff_stk2idx_zsj_if(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close','open', 'low', 'high', 'amount']
    normalize_size = 3000 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        #stk_close = data['close_preadj'].iloc[-75:].values
        stk_high = data['high_preadj'].iloc[-75:].values
        stk_low = data['low_preadj'].iloc[-75:].values
        stk_open = data['open_preadj'].iloc[-75:].values
        #stk_amount = data['amount_preadj'].iloc[-75:].values
        
        roll_win = 45
        #ma_win = 15
        #ts_pct_win = 3000
        #min_pct = 0.9
        min_periods = int(0.5 * roll_win)
        high_open_diff = stk_high - stk_open
        open_low_diff = stk_open - stk_low

        high_low_diff_stk = bk.move_sum(high_open_diff, roll_win, min_count = min_periods, axis = 0) - bk.move_sum(open_low_diff, roll_win, min_count = min_periods, axis = 0)
        high_low_diff_stk2idx_raw = np.nanmean(high_low_diff_stk, axis = 1)
        #factor = calc_ma_helper(high_low_diff_stk2idx_raw, ma_win, ts_pct_win, min_pct)[-1]
        factor  = np.nanmean(high_low_diff_stk2idx_raw[-15:])
        return factor