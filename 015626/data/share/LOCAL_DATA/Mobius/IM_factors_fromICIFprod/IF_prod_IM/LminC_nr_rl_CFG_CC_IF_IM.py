# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:56:39 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

      
class LminC_nr_rl_CFG_CC_IF_IM(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'low']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(0, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-46:]          
        tover[abs(tover) < 1e-8] = np.nan
        ret_30 = (tover/tover.shift(30)-1).iloc[-15:]
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.90, axis = 1)), axis=0)     
        mask = temp5

        hlow = data['low_preadj'].iloc[-1400:].values
        hclose = data['close_preadj'].iloc[-1400:].values
        
        lltc_ind_r = -bk.move_min(hlow, 180, min_count = 90, axis = 0)/hclose
        lltc_ind_r = rolling_norm(lltc_ind_r)[-15:]
        tempdf = (lltc_ind_r*mask)
        tempdf = np.nansum(tempdf, axis = 1)
        factor = np.nanmean(tempdf)
        
        return factor