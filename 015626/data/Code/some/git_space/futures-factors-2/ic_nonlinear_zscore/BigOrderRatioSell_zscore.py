# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 19:00:37 2022

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class BigOrderRatioSell_zscore(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['sell_superorder_count', 'sell_bigorder_count', 'sell_midorder_count', 'sell_smallorder_count']
    normalize_size = 14400
    normalize_type = 'zscore'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['sell_superorder_count'].iloc[-1]
        big = data['sell_bigorder_count'].iloc[-1]
        mid = data['sell_midorder_count'].iloc[-1]
        small = data['sell_smallorder_count'].iloc[-1]

        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        temp = cross4(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(big/temp)
        
        return factor