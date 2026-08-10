# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:53:01 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

   

class Crossing_Turns_tr_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','open', 'amount','volume','close','turnover_rate', 'high', 'low']
    normalize_size = 1200 # normalize所用历史数据长度'
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-66:]
        turnover = tover.rolling(60, min_periods = 15).mean()
        turnover_rank = (2 * turnover.rank(axis=1, pct=True) - 1).values[-5:]

        hopen = data['open_preadj'].iloc[-63:].values
        hhigh = data['high_preadj'].iloc[-63:].values
        hclose = data['close_preadj'].iloc[-63:].values
        hlow = data['low_preadj'].iloc[-63:].values
        
        temp = np.abs(np.where(hopen-hclose == 0, 0.1, hopen-hclose))

        temp0 = (hhigh - hlow)
        temp1 = temp0/temp
        v1 = data['volume_preadj'].iloc[-64:].values
        v1[abs(v1) < 1e-8] = np.nan
        amount = data['amount'].iloc[-64:].values
        vwap = amount/v1
        a = bk.move_sum((vwap[1:]/vwap[:-1]-1), 30, min_count = 15, axis = 0)
        vwtc_r = bk.move_mean((temp1*(a)), 25, min_count = 5, axis = 0)[-5:]

        tempdf = np.nanmean(np.nanmean((vwtc_r*turnover_rank), axis = 1))

        return tempdf