# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:53:09 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class CFG7_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['turnover_rate', 'close', 'open', 'adjfactor']
    #data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        to = data['turnover_rate'].iloc[-120:]
        hclose = data['close_preadj'].iloc[-120:]
        
        hopen = data['open_preadj'].iloc[-120:]
        ret = hclose/hopen -1
        hret = hclose/hclose.shift(1) -1
        cc1 = ((to[hclose<hopen]/abs(ret[hclose<hopen])))
        #ccc1 = cc1.rolling(60, min_periods = 7).mean()
        ccc1 = pd.DataFrame(bk.move_mean(cc1, 60, min_count = 7, axis = 0), index = cc1.index, columns = cc1.columns)
        cc2 = to_ts(ccc1, hret)
        ccc2 = np.nanmean(cc2.iloc[-60:])
        return ccc2