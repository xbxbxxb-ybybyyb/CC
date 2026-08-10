# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:57:48 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class SYXWR_nr_wt_CFG_CC_IF_IH(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'weight','turnover_rate', 'low', 'high', 'open']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-105:]
        temp = bk.move_mean(tover, 60, min_count = 15, axis = 0)
        turnover = pd.DataFrame(temp,index = tover.index, columns = tover.columns).iloc[-45:]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values
        
        stk_weight = (data['weight']).iloc[-45:].values
        mask = stk_weight*temp4

        hopen = data['open_preadj'].iloc[-75:].values
        hclose = data['close_preadj'].iloc[-75:].values 
        hhigh = data['high_preadj'].iloc[-75:].values
        hlow = data['low_preadj'].iloc[-75:].values 
        
        temp1 = (np.where(hopen>hclose, hopen, hclose))
        
        b = bk.move_mean((hhigh - temp1), 30, min_count = 15, axis = 0)
        b[abs(b)<1e-8] = np.nan
        t_pcor = (hhigh - temp1)/b
        h = bk.move_max(hhigh, 30, min_count = 15, axis = 0)
        l = bk.move_min(hlow, 30, min_count = 15, axis = 0)
        a = h-l
        t_pcor2 = (hclose-l)/a
        t_pcorr = np.nansum(((t_pcor2 - t_pcor)[-45:])*mask, axis = 1)
        
        factor = np.nanmean(t_pcorr)
        return factor