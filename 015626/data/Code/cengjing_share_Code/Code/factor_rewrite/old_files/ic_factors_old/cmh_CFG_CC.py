# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:04:57 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


#
class cmh_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','high','adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀

    def calculate(self, data):
        
        index_close = data['close_000905.SH'].iloc[-2208:]
        stk_close = data['close_preadj'].iloc[-2208:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = (stk_ret.iloc[-2206:].rolling(1200, min_periods=600).corr(index_ret.iloc[-2206:,0]))
        
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        bool_df = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0).astype(float).values[-1005:]
        bool_df[bool_df==0] = np.nan
        

        hhigh = data['high_preadj'].iloc[-2270:].values  
        hclose = data['close_preadj'].iloc[-2270:].values 
        
        vwtc_r = (hhigh-bk.move_mean(hclose, 60, min_count = 30, axis = 0))[-1005:]
 
        factor = np.nanmean(vwtc_r*bool_df, axis = 1)
        
        factor = ts_rank(factor, 1000)
        factor = np.nanmean(factor[-2:])
               
        return factor
