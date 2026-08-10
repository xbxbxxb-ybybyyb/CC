# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 11:19:55 2022

@author: appadmin
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:58:53 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
import numpy.ma as ma

class BSW_1_CC_IF(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'WeightBuyOrderQtySumMean', 'WeightSellOrderQtySumMean','BuyNumOrdersSumMean','SellNumOrdersSumMean', 'close']
    normalize_size = 1000
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        df_s1 = bk.move_mean(data['BuyNumOrdersSumMean'].values[-41:] / r(data['WeightBuyOrderQtySumMean'].values[-41:]), 30, 2, axis = 0)      
        df_s2 = bk.move_mean(data['SellNumOrdersSumMean'].values[-41:] / r(data['WeightSellOrderQtySumMean'].values[-41:]), 30, 2, axis = 0)
        df_s = ((df_s1 + df_s2)[-10:])*(data['weight'].values[-10:])
        
        hclose = data['close'].values[-22:]
        hret = hclose[1:]/hclose[:-1] - 1
        hret[abs(hret)>10000] = np.nan
        hret = bk.move_mean(hret, 10, 1, axis = 0)[-10:]
        
        df_s_mask = np.nanmedian(df_s, axis = 1)
        df_s_mask = np.expand_dims(df_s_mask, axis=-1)
        hret_1 = ma.array(hret, mask=(df_s<=df_s_mask))
        hret_2 = ma.array(hret, mask=(df_s>=df_s_mask))
        temp2 = np.nanmean(hret_1, axis = 1) - np.nanmean(hret_2, axis = 1)    
        temp2 = np.nanmean(temp2)
        return temp2
