# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:59:02 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class hhll_nr_we_CC_CFG_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','weight', 'turnover_rate', 'low', 'high']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-95:]          
        tover[abs(tover) < 1e-8] = np.nan
        ret_30 = (tover/tover.shift(30)-1).iloc[-60:]
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0)
        stk_weight = (data['weight']).iloc[-60:].values
        
        mask = temp5*stk_weight
        
        hhigh = data['high_preadj'].iloc[-1275:].values
        hlow = data['low_preadj'].iloc[-1275:].values
        
        d1 = (hhigh[1:]>hhigh[:-1])
        d2 = (hlow[1:]>hlow[:-1])
        
        d_f = (d1.astype(int)+d2.astype(int))
        d_f[d_f == 2] = 4
        
        factor1 = rolling_norm(d_f, 242*5)[-60:]
    
        factor = np.nansum(factor1*mask, axis = 1)
        
        factor = np.nanmean(factor)
    
        return factor
