# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 14:50:24 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import scipy


class Short_HDLD_CFG2_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 9
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'close','low','high', 'open', 'adjfactor']

    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

       
        
        hclose = data['close_preadj'].iloc[-31:].values
        hopen = data['open_preadj'].iloc[-1].values
        
        hlow = data['low_preadj'].iloc[-1].values
        hhigh = data['high_preadj'].iloc[-1].values
        
        stk_weight = data['weight'].iloc[-1].values
        
        temp = np.abs(hclose[-1]-hopen)
        temp[temp==0] = 0.01
        
        temp0 = (hhigh - hlow)
        temp1 = (temp0/temp)
        a = np.nansum(hclose[1:]/hclose[:-1]-1, axis = 0)
        vwtc_r = (temp1*(a))*stk_weight

        return np.nanmean(vwtc_r)