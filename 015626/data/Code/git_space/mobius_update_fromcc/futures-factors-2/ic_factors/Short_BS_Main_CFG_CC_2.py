# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 13:43:47 2022

@author: appadmin
"""
import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
from operators_wsc_1_0 import *
import pandas as pd

class Short_BS_Main_CFG_CC_2(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight','BuyUniqueOrderNum','BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 240 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        try:
            BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-1]
            BuyTradeNum = data['BuyTradeNum'].values[-1]
            SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-1]
            SellTradeNum = data['SellTradeNum'].values[-1]
            
            factor_raw = BuyUniqueOrderNum/r(BuyTradeNum) - SellUniqueOrderNum/r(SellTradeNum)
            
            df_s = data['weight'].values[-1]
            amount_mask = np.nanquantile(df_s, 0.9)
            amount_mask = np.expand_dims(amount_mask, axis=-1) 
            factor_raw_after_mask = ma.array(factor_raw, mask=(df_s<=amount_mask))
            factor_raw_after_mask = np.nanmean(factor_raw_after_mask)
            factor = np.nanmean(factor_raw_after_mask)
            return float(-factor)
        except:
        	return np.nan
    
