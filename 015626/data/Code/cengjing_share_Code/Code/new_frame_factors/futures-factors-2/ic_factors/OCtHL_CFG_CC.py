# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:02:46 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class OCtHL_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'low', 'high','open', 'amount', 'adjfactor']
    normalize_size = 1000 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        

        hopen = data['open_preadj'].iloc[-120:].values
        hhigh = data['high_preadj'].iloc[-120:].values
        hclose = data['close_preadj'].iloc[-120:].values
        hlow = data['low_preadj'].iloc[-120:].values
        hamount = data['amount'].iloc[-120:]
        
        df_s = hamount.sum(axis = 0)

        stk_amount = df_s.gt((df_s.quantile(0.90)))
        temp1 = hopen - hclose
        temp2 = hhigh - hlow
        t_pcor2 = -temp1/temp2
        t_pcor2[abs(t_pcor2)>10000] = np.nan
        t_pcor2 = bk.move_mean(t_pcor2, 45, min_count = 15, axis =0)#.rolling(5, min_periods = 2).mean()
        factor = (t_pcor2[-1]*stk_amount).mean()
        
        return factor