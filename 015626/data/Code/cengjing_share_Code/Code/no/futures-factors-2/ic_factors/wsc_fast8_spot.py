# -*- coding: utf-8 -*-
"""
Created on Mon Feb  7 17:50:27 2022

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_wsc_1_0 import *
import pandas as pd


class wsc_fast8_spot(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Index_Id'] = {'000905.SH':['close', 'volume']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        index_close = data['close_000905.SH'].values[-55:]
        index_volume = data['volume_000905.SH'].values[-55:]

        ret = ts_pct_change(index_close, 1)
        log_ret = log(ret+1)
        ret_std = bk.move_std(ret, 15, 2, axis = 0)
        log_ret_weight = log_ret / index_volume * ret_std
        factor_raw = bk.move_sum(log_ret_weight, 30, 2, axis = 0)
        factor = np.nanmean(factor_raw[-3:])
        
        return factor