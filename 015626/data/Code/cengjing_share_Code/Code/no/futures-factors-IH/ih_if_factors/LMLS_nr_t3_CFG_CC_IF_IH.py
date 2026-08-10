# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:56:02 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    
class LMLS_nr_t3_CFG_CC_IF_IH(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'low']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-80:]       
        turnover = (tover.rolling(60, min_periods = 15).mean()).iloc[-15:]
        hclose = data['close_preadj'].iloc[-70:]       
        ret = (hclose/hclose.shift(30)-1).iloc[-15:]
        
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values
        temp6 = ret.gt(pd.Series(ret.quantile(0.80, axis = 1)), axis=0).values   
        mask = (temp4*temp6).astype(float)
        
        hlow = data['low_preadj'].iloc[-1276:].values
        hlow_s = data['low_preadj'].iloc[-1322:].shift(15).values[-1276:]
        
        temp = bk.move_mean(hlow, 60, min_count = 15, axis = 0) - bk.move_mean(hlow_s, 45, min_count = 15, axis = 0)
        temp = rolling_norm(temp)[-15:]
        factor = np.nanmean(np.nansum(temp*mask, axis = 1))
        
        return factor