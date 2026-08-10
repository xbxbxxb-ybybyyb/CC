# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:52:20 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class CFG23_CC_IH(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor']
    data_dict['Index_Id'] = {'000016.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        index_close = data['close_000016.SH'].iloc[-1203:]
        stk_close = data['close_preadj'].iloc[-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:, 0])
        #stk_index_corr = ((stk_ret.iloc[-1201:]).rolling(1200, min_periods=600).corr(index_ret.iloc[-1201:, 0])).iloc[0]
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        bool_df = stk_index_corr.gt(stk_index_corr.quantile(0.90)).astype(float)
        #bool_df = (stk_index_corr.argsort().argsort()>=(np.shape(stk_index_corr)[-1]*0.9))
        temp = pd.Series(np.array(range(len(bool_df))))
        temp.index =  bool_df.index
        temp.name =  bool_df.name

        stk_close = stk_close.iloc[-61:]
        x = np.array(range(len(stk_close)))
        holder = {}
        for item in stk_close.columns:
            close_spot = stk_close[item].values
            holder[item] = pd.Series(rolling_linear_reg(x, close_spot, 60))
        temp1 = pd.DataFrame(holder)
        temp1.index = stk_close.index
        #print(bool_df.sum())
        temp = ((temp1.iloc[-1])*bool_df).mean()
        
        return temp