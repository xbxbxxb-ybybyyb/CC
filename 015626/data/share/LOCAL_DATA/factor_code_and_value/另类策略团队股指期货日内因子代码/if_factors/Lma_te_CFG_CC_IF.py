# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:56:20 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class Lma_te_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'low']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-1330:]       
        temp = bk.move_mean(tover, 60, min_count = 15, axis = 0)
        turnover = pd.DataFrame(temp, index= tover.index, columns = tover.columns).iloc[-1220:]
        ret_30 = (tover/tover.shift(30)-1).iloc[-1220:]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0)     
        mask = temp4*temp5

        hlow = data['low_preadj'].iloc[-1330:]
        hclose = data['close_preadj'].iloc[-1330:]
        
        vwtc_r = (hlow-bk.move_mean((hclose), 120, min_count = 30, axis = 0))[-1220:]
        tempdf = np.nansum(vwtc_r*mask, axis = 1)
        
        factor = bk.move_mean(tempdf, 8, min_count = 2, axis = 0)
        factor = ts_rank(factor)
        factor = np.nanmean(factor[-3:])
        
        return factor