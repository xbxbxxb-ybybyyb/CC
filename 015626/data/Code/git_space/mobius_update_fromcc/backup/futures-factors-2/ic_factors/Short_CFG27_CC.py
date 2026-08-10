# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 14:15:05 2022

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
import bottleneck as bk
from operators_cc import *
import pandas as pd
from operators_wsc_1_0 import *

class Short_CFG27_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close','volume', 'adjfactor', 'high', 'low']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hclose = data['close_preadj'].values[-96:]
        hhigh = data['high_preadj'].values[-96:]
        hlow = data['low_preadj'].values[-96:]
        hvolume = data['volume_preadj'].values[-96:]
        hret = ts_pct_change(hclose, 1)[-25:]
        
        temp1 = bk.move_max(hhigh, 30, 7, axis = 0)-hclose
        temp2 = hclose-bk.move_min(hlow, 30, 7, axis = 0)

        temp11 = (temp1>temp2)
        temp22 = (temp2>=temp1)
        
        temp = temp11*temp1 + temp22*temp2
        i1 = bk.move_mean(temp*hvolume, 20, 2, axis = 0)[-25:]
        
        df_s_mask = np.nanmedian(i1, axis=1)
        df_s_mask = np.expand_dims(df_s_mask, axis=-1)
        hret1 = ma.array(hret, mask=(i1 - df_s_mask <= 1e-9))
        hret2 = ma.array(hret, mask=(i1 - df_s_mask >= 1e-9))
        factor = np.nanmean(hret1, axis=1) - np.nanmean(hret2, axis=1)
        return np.nanmean(factor)