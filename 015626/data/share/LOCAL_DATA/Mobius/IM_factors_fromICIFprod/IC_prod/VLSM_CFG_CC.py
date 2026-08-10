# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:03:59 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class VLSM_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','amount', 'low', 'high','open', 'weight','volume', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀

    def calculate(self, data):
        
        hopen = data['open_preadj'].iloc[-85:].values
        hhigh = data['high_preadj'].iloc[-85:].values
        hclose = data['close_preadj'].iloc[-85:].values
        hlow = data['low_preadj'].iloc[-85:].values
        
        amount = data['amount'].iloc[-120:]
        df_s = amount.sum(axis = 0)
        stk_amount = df_s.gt(df_s.quantile(0.90)).astype(float)
        stk_amount[stk_amount==0] = np.nan
        
        temp1 = (np.where(hopen>hclose, hopen, hclose))
        
        b = bk.move_mean((hhigh - temp1), 40, min_count = 15, axis = 0)
        b[abs(b)<1e-8] = np.nan
        t_pcor = (hhigh - temp1)/b
        h = bk.move_max(hhigh, 40, min_count = 15, axis = 0)
        l = bk.move_min(hlow, 40, min_count = 15, axis = 0)
        a = h-l
        a[abs(a) < 1e-8] = np.nan
        t_pcor2 = (hclose-l)/a
        t_pcorr = bk.move_mean((t_pcor2 - t_pcor)[-41:], 40, min_count = 20, axis = 0)[-1]
        t = np.nanmean(t_pcorr*stk_amount)
        
        return t