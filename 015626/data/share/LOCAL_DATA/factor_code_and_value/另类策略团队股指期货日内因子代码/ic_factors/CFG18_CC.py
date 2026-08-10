# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:48:36 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class CFG18_CC(FutureFactor):
    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['high','close','weight','adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        hclose = data['close_preadj'].iloc[-48:]
        hweight = data['weight'].iloc[-48:]

        
        hret = hclose/hclose.shift(1)-1
        htemp = (hret*hweight).mean(axis = 1)
        htemp = bk.move_mean(htemp, 45, min_count = 15, axis = 0)
        #htemp = bk.move_mean((hhigh>bk.move_max(hhigh, 45, min_count = 5, axis = 0)), 90, min_count = 5, axis = 0)
        factor = htemp[-1]        
        return factor