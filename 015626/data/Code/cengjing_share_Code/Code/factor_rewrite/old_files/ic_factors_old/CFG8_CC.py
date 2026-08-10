# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:53:36 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class CFG8_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = ['float_shares', 'volume', 'close', 'adjfactor']
    #data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        hvolume = data['volume_preadj'].iloc[-31:]
        hclose = data['close_preadj'].iloc[-31:]
        hfs = data['float_shares'].iloc[-31:]
        hret = hclose/hclose.shift(1) - 1
        d1 = hvolume/hclose/hfs
        d1 = to_ts(d1, hret)
        dd1 = np.nanmean(d1.iloc[-30:])
        return dd1