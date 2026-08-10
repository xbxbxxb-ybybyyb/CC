# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 09:58:11 2022

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk


class BSW_2_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'WeightBuyOrderQtySumMean', 'WeightSellOrderQtySumMean','BuyNumOrdersSumMean','SellNumOrdersSumMean', 'close']
    normalize_size = 2000
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        df_s1 = bk.move_mean(data['BuyNumOrdersSumMean'].values[-35:] / r(data['WeightBuyOrderQtySumMean'].values[-35:]), 30, 2, axis = 0)      
        df_s2 = bk.move_mean(data['SellNumOrdersSumMean'].values[-35:] / r(data['WeightSellOrderQtySumMean'].values[-35:]), 30, 2, axis = 0)
        df_s = ((df_s1 + df_s2)[-4:])*(data['weight'].values[-4:])
        
        hclose = data['close'].values[-7:]
        hret = hclose[1:]/hclose[:-1] - 1
        hret[abs(hret)>10000] = np.nan
        hret = bk.move_mean(hret, 2, 1, axis = 0)[-4:]
        
        df_s_mask = np.nanmedian(df_s, axis = 1)
        df_s_mask = np.expand_dims(df_s_mask, axis=-1)
        hret_1 = ma.array(hret, mask=(df_s<=df_s_mask))
        hret_2 = ma.array(hret, mask=(df_s>=df_s_mask))
        temp2 = np.nanmean(hret_1, axis = 1) - np.nanmean(hret_2, axis = 1)    
        temp2 = np.nanmean(temp2)
        return temp2