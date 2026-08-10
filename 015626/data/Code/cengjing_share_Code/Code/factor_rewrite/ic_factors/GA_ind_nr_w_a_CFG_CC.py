# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:55:28 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class GA_ind_nr_w_a_CFG_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = [ 'amount', 'weight', 'close','low','high', 'open', 'adjfactor']
    #data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 242 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        amount = data['amount'].iloc[-120:]
        df_s = amount.sum(axis = 0)
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80)).iloc[0]).values
        stk_weight = data['weight'].iloc[-1].values
        bool_df = (stk_weight*temp1)
        
        hhigh = data['high_preadj'].values[-370:]
        hclose = data['close_preadj'].values[-370:]
        hlow = data['low_preadj'].values[-370:]
        o= data['open_preadj'].iloc[-370:].shift(120).values
        h = bk.move_max(hhigh, 120, min_count = 60, axis = 0)
        l = bk.move_min(hlow, 120, min_count = 60, axis = 0)
        
        a = h-o
        b = hclose - l 
        c = (h-l)*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = ((a+b)/c)
        vwtc_r = rolling_norm(vwtc_r, 242)[-1]
        factor = np.nanmean(vwtc_r*bool_df)
        return factor