# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 13:33:43 2021

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import *
from future_factor import FutureFactor
import pandas as pd

    
class Short_CFG8_CC_IM(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['float_shares', 'volume', 'close', 'adjfactor']
    #data_dict['Index_Id'] = {'000852.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    #num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        hvolume = data['volume_preadj'].values[-30:]
        hclose = data['close_preadj'].values[-31:]
        hfs = data['float_shares'].values[-30:]
        hret = hclose[1:]/hclose[:-1] - 1
        d1 = hvolume/hfs
        
        df_s_mask = np.nanmedian(d1, axis = 1)
        df_s_mask = np.expand_dims(df_s_mask, axis = -1)
        hret_1 = ma.array(hret, mask=(d1 - df_s_mask<= 1e-9))
        hret_2 = ma.array(hret, mask=(d1 - df_s_mask>= 1e-9))
        temp2 = np.nanmean(hret_1, axis = 1) - np.nanmean(hret_2, axis = 1)

        dd1 = np.nanmean(temp2)
        return dd1