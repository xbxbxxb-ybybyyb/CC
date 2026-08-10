# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 17:17:01 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class BuyUnique_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        a = data['BuyUniqueOrderNum'].iloc[-240:]

        date = str(a.index.date[-1])
        a1 = a.loc[date].values
        a2 = data['BuyTradeNum'].loc[date].values
        if len(a1)<=5:
            if len(a1) == 1:
                pass
            else:
                a1 = np.nanmean(a1, axis = 0)
                a2 = np.nanmean(a2, axis = 0)
        else:
            a1 = np.nanmean(a1[-5:], axis = 0)
            a2 = np.nanmean(a2[-5:], axis = 0)
            
        a2[abs(a2)<1e-8] = np.nan
        a = cross(a1/a2)

        factor = np.nanmean(a)
        
        return factor