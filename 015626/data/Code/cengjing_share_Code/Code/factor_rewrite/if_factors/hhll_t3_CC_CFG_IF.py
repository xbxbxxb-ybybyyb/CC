# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:59:20 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

   
class hhll_t3_CC_CFG_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'low', 'high']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        
        tover = data['turnover_rate'].iloc[-135:]
        close_mask = data['close_preadj'].iloc[-95:]
        temp = bk.move_mean(tover, 60, min_count = 15, axis = 0)
        turnover = pd.DataFrame(temp,index = tover.index, columns = tover.columns).iloc[-60:]
        ret = (close_mask/close_mask.shift(30)-1).iloc[-60:]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        temp6 = ret.gt(pd.Series(ret.quantile(0.80, axis = 1)), axis=0)
        mask = temp4*temp6
        
        hhigh = data['high_preadj'].iloc[-65:].values
        hlow = data['low_preadj'].iloc[-65:].values
        
        d1 = (hhigh[1:]>hhigh[:-1])
        d2 = (hlow[1:]>hlow[:-1])
        
        d_f = (d1.astype(int)+d2.astype(int))
        d_f[d_f == 2] = 4
        
        factor1 = d_f[-60:]

        factor = np.nansum(factor1*mask, axis = 1)
        
        factor = np.nanmean(factor)

        return factor