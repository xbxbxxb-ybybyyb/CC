# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:55:10 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class GA_CFG_CC_IH(FutureFactor):
  
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'amount', 'close','low','high', 'open', 'adjfactor']
    #data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        amount = data['amount'].iloc[-120:]
        df_s = amount.sum(axis = 0)
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90)).iloc[0]).values.astype(float)
        bool_df[bool_df==0] = np.nan
        
        hhigh = data['high_preadj'].values[-120:]
        hclose = data['close_preadj'].values[-120:]
        hlow = data['low_preadj'].values[-120:]
        o= data['open_preadj'].iloc[-125:].shift(120).values[-1]
        h = np.nanmax(hhigh, axis = 0)
        l = np.nanmin(hlow, axis = 0)
        
        a = h-o
        b = hclose - l 
        c = (h-l)*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = ((a+b)/c)[-1]
        factor = np.nanmean(vwtc_r*bool_df)
        return factor