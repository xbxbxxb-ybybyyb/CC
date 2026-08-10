# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:06:11 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



#
class hhll_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['amount', 'low', 'high', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        hamount = data['amount'].iloc[-120:]
        df_s = hamount.sum(axis = 0)
        stk_amount = df_s.gt(df_s.quantile(0.90)).astype(float)
        stk_amount[stk_amount==0] = np.nan

        hhigh = data['high_preadj'].iloc[-45:].values
        hlow = data['low_preadj'].iloc[-45:].values
        
        d1 = hhigh[1:]>hhigh[:-1]
        d2 = hlow[1:]>hlow[:-1]
        
        d_f = (d1.astype(int)+d2.astype(int))
        d_f[d_f == 2] = 4
        
        vwtc_r = np.nanmean(d_f[-25:], axis = 0)
        factor = np.nanmean(vwtc_r*stk_amount)
        
        return factor