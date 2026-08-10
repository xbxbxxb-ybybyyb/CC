# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:49:36 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class CFG20_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = ['high','low','close','weight', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '[0, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hlow = data['low_preadj'].values[-1000:]
        hhigh = data['high_preadj'].values[-1000:]
        hclose = data['close_preadj'].values[-1000:]
        hweight = data['weight'].values[-1000:]
        
        h = bk.move_max(hhigh, 90, min_count = 10, axis = 0)
        l = bk.move_min(hlow, 90, min_count = 10, axis = 0)
        
        r =  h - l
        r[abs(r)<1e-8] = np.nan
        
        hh = (h - hclose)/r 

        ll = (hclose - l)/r
        vwtc_r = bk.move_mean(ll, 20, min_count = 5, axis = 0)
        vw = bk.move_mean(hh, 20, min_count = 5, axis = 0)
        
        a = vwtc_r-vw
        
        htemp = np.nanmean((a*hweight), axis = 1)
        htemp = rolling_norm(htemp, 242*3)
        htemp[abs(htemp)>1] = 0
        htemp = np.nanmean(htemp[-3:])
        return htemp