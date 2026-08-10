# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 09:36:57 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class MidOrderRatioSellMoney_Weighted_IH(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['sell_superorder_money', 'sell_bigorder_money', 'sell_midorder_money', 'sell_smallorder_money', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['sell_superorder_money'].iloc[-1]
        big = data['sell_bigorder_money'].iloc[-1]
        mid = data['sell_midorder_money'].iloc[-1]
        small = data['sell_smallorder_money'].iloc[-1]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        sup = sup.values
        big = big.values
        mid = mid.values
        small = small.values
        
        temp = cross4(sup+big + mid + small)
        
        factor = np.nanmean(data['weight'].iloc[-1]*mid/temp)
        
        return factor