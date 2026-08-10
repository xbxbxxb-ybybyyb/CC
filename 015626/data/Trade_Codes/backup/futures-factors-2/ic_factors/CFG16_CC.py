# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:08:30 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class CFG16_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','low', 'adjfactor']
    normalize_size = 1200# normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        hlow = data['low_preadj'].iloc[-1320:].values
        hclose = data['close_preadj'].iloc[-1321:].values
        hret = hclose[1:]/hclose[:-1]-1
        i1 = -bk.move_min(hlow, 60, min_count = 15, axis = 0)/bk.move_mean(hlow, 30, min_count = 10, axis = 0)
        i1 = pd.DataFrame(i1, index =  data['low_preadj'].iloc[-1320:].index, columns = data['low_preadj'].columns)
        #hret = pd.DataFrame(hret, index =  data['low_preadj'].iloc[-1320:].index, columns = data['low_preadj'].columns)
        i2 = to_ts(i1, hret)
        i2 = rolling_norm(bk.move_mean(i2, 30, min_count = 15, axis = 0), method = 'ts_rank')

        factor = np.nanmean(i2[-5:])
        return factor