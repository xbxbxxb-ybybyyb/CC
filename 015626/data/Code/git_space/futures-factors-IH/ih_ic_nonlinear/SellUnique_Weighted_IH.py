# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 10:40:33 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class SellUnique_Weighted_IH(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['SellUniqueOrderNum', 'SellTradeNum', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        a = data['SellUniqueOrderNum'].iloc[-1]
        b = data['SellTradeNum'].iloc[-1]
        w = data['weight'].iloc[-1].values
        #a.fillna(0, inplace = True)
        #b.fillna(0, inplace = True)
        
        a = a.values
        b = b.values
        temp = cross(a/b)
        
        factor = np.nanmean(w*temp)
        
        return factor