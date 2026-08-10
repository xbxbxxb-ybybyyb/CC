# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:57:31 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



class RS_ind_wt_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'weight']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-70:]
        temp = bk.move_mean(tover, 60, min_count = 15, axis = 0)
        turnover = pd.DataFrame(temp,index = tover.index, columns = tover.columns).iloc[-8:]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values
        
        stk_weight = (data['weight']).iloc[-8:].values
        wt = stk_weight*temp4

        hclose = data['close_preadj'].iloc[-35:]
        ret = (hclose.values)[1:]/(hclose.values)[:-1]
        a = bk.move_std(ret, 25, min_count = 15, axis = 0)[-8:]
        a[abs(a)<1e-8] = np.nan     
        hclose_s = hclose.shift(24).iloc[-8:].values
        
        i1 = (((hclose.values)[-8:])/hclose_s-1) / a

        tempdf = np.nansum((i1*wt), axis = 1)

        factor = np.nanmean(tempdf)
        return factor
