# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:54:31 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class CrossingTurns_CFG_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = [ 'amount', 'close', 'open', 'high', 'low','adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        amount = data['amount'].iloc[-120:]
        df_s = amount.sum(axis = 0)
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90)).iloc[0])
        
        index_close = data['close_000905.SH'].iloc[-1203:]
        stk_close = data['close_preadj'].iloc[-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:, 0])
        stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90)).iloc[0])
        bool_df = (stk_index_corr*stk_amount).values.astype(float)
        bool_df[bool_df==0] = np.nan
        
        hclose = data['close_preadj'].values[-45:]
        hopen = data['open_preadj'].values[-45:]
        
        hhigh = data['high_preadj'].values[-45:]
        hlow = data['low_preadj'].values[-45:]
        
        temp = np.abs(hclose-hopen)
        temp[temp==0] = 0.01
        #temp.index = hclose.index
        temp0 = (hhigh - hlow)
        temp1 = (temp0/temp)[-15:]
        a = (bk.move_sum((hclose[1:]/hclose[:-1]-1), 30, min_count = 15, axis = 0))[-15:]
        vwtc_r = np.nanmean((temp1*(a)), axis = 0)

        factor = np.nanmean(vwtc_r*bool_df)
        
        return factor