# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:07:53 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


        
class vol_diff_zsj_IH(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close','volume']
    normalize_size = 242*5 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.85, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        stk_close = data['close_preadj'].iloc[-61:].values
        stk_volume = data['volume_preadj'].iloc[-60:].values
        stk_close[abs(stk_close) < 1e-8] = np.nan
        
        stk_ret = (stk_close[1:] / stk_close[:-1] - 1)
        up_mask = (stk_ret > 0).astype(float)
        down_mask = (stk_ret < 0).astype(float)
        up_vol = np.nansum(stk_volume*up_mask, axis = 1)
        down_vol = np.nansum(stk_volume*down_mask, axis = 1)
        vol_diff_raw = up_vol - down_vol
        factor = np.nanmean(vol_diff_raw)
        return factor