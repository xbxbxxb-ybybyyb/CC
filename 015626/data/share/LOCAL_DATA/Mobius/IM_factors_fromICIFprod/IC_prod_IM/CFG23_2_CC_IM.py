# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:51:58 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class CFG23_2_CC_IM(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor', 'amount']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-121:]
        close = data['close_preadj'].iloc[-46:]
        df_s = amount.rolling(120, min_periods = 5).sum()
        bool_df = (df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)).values[-46:].astype(float)
        bool_df[bool_df==0] = np.nan
        x = np.array(range(len(close)))
        holder = {}
        for item in close.columns:
            close_spot = close[item].values
            holder[item] = pd.Series(rolling_linear_reg(x, close_spot, 45))
        temp1 = pd.DataFrame(holder)
        temp1.index = close.index
        temp = (temp1*bool_df).mean(axis = 1)
        
        return temp.iloc[-1]