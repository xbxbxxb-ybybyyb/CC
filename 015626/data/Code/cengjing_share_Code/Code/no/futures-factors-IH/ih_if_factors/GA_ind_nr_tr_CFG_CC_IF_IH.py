# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:53:17 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


    

class GA_ind_nr_tr_CFG_CC_IF_IH(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 8
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','open', 'high','close','turnover_rate', 'low']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-66:]
        turnover = tover.rolling(60, min_periods = 15).mean()
        mask = (2 * turnover.rank(axis=1, pct=True) - 1).values[-5:]
        
        hopen = data['open_preadj'].iloc[-1340:].values
        hhigh = data['high_preadj'].iloc[-1340:].values
        hclose = data['close_preadj'].iloc[-1340:].values
        hlow = data['low_preadj'].iloc[-1340:].values
        
        h = bk.move_max(hhigh, 120, min_count = 60, axis = 0)[-1210:]
        l = bk.move_min(hlow, 120, min_count = 60, axis = 0)[-1210:]
        
        a = h-(hopen[:-120])[-1210:]
        b = hclose[-1210:] - l[-1210:]
        c = (h-l)*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = (a+b)/c
        vwtc_r = rolling_norm(vwtc_r)[-5:]
        tempdf = np.nanmean(np.nansum(vwtc_r*mask, axis = 1))

        return tempdf