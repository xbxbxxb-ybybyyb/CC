# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:49:01 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class CFG1_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount','close','weight', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-156:]
        df_s = amount.rolling(120, min_periods = 5).sum()
        bool_df = (df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)).values
        hclose = data['close_preadj'].values[-38:]
        weight = data['weight'].values[-38:]

        hret = (hclose[1:]/hclose[:-1]-1)
        temp_weighted = hret[-36:]*weight[-36:]*bool_df[-36:]
        a = bk.move_mean(np.nanmean(temp_weighted, axis = 1), 35, min_count = 15)
        return a[-1]
