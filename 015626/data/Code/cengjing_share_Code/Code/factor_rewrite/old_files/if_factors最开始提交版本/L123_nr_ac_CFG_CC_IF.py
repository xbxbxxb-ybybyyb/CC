# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:54:37 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    

class L123_nr_ac_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','amount', 'stk_index_corr_hs300', 'low']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-166:]
        df_s = amount.rolling(120, min_periods = 15).sum().iloc[-45:]
        stk_index_corr = data['stk_index_corr_hs300'].iloc[-45:]        
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0).values
        temp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0).values
        mask = (temp1*temp2)
        
        hlow = data['low_preadj'].iloc[-1285:].values
        i11 = (bk.move_min(hlow, 10, min_count = 5, axis = 0)-bk.move_min(hlow, 25, min_count = 10, axis = 0))
        i12 = bk.move_min(hlow, 20, min_count = 15, axis = 0)-bk.move_min(hlow, 30, min_count = 10, axis = 0)
        i2 = (i11-i12)
        i2 = rolling_norm(i2, 242*5)[-45:]
        tempdf = np.nanmean(i2*mask, axis = 1)
        factor = np.nanmean(tempdf)
        
        return factor
    