# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:50:29 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


    
    
class CFG29_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor', 'close']
    normalize_size = 400 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hclose = data['close_preadj'].iloc[-75:].values
        temp1 = bk.move_max(hclose, 35, min_count = 20, axis = 0)[-36:]
        holder = {}
        for i, item in enumerate(temp1.T):
            x = np.array(range(len(item)))
            holder[i] = pd.Series(rolling_linear_reg(x, item, 35))
        
        factor = pd.DataFrame(holder).mean(axis = 1).iloc[-1]
        return factor