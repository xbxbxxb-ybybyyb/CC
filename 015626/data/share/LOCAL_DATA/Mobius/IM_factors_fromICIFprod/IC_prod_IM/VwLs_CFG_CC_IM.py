# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:18:43 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class VwLs_CFG_CC_IM(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['amount','volume', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀

    def calculate(self, data):
        

        hamount = data['amount'].iloc[-120:]
        hvolume = data['volume_preadj'].iloc[-120:].values      

        df_s = hamount.sum(axis = 0)
        bool_df = df_s.gt(df_s.quantile(0.90)).values
        
        hamount = hamount.values
        
        vwap = hamount/hvolume
        price_diff_1 = (vwap[1:]/vwap[:-1]-1)[-5:]
        price_diff_90 = (vwap[90:]/vwap[:-90]-1)[-5:]
        copcor1_r = -np.nanmean((price_diff_1-price_diff_90), axis = 0)
        
        factor = np.nanmean(bool_df*copcor1_r)

        return factor