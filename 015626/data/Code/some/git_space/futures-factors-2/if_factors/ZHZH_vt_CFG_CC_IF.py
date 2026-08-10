# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:58:06 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class ZHZH_vt_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'high']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-75:]
        temp = bk.move_mean(tover, 60, min_count = 15, axis = 0)
        turnover = pd.DataFrame(temp,index = tover.index, columns = tover.columns).iloc[-15:]
        
        stk_close = data['close_preadj'].iloc[-50:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30).iloc[-15:]
        
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values 
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0).values
        mask = temp3*temp4

        hhigh = data['high_preadj'].iloc[-120:].values
        h = bk.move_max(hhigh, 10, min_count = 5, axis = 0)
        hc = bk.move_mean(((hhigh >= h).astype(int)), 90, min_count = 5, axis = 0)[-15:]
        
        factor = np.nanmean(np.nanmean(hc*mask, axis = 1))
        
        return factor