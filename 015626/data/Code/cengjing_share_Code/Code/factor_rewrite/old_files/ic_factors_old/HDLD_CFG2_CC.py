# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 10:51:09 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from operators_cc import *
import pandas as pd

class HDLD_CFG2_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 9
    data_dict = dict()
    data_dict['Stock'] = [ 'amount', 'weight', 'close','low','high', 'open', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        index_close = data['close_000905.SH'].iloc[-2001:]
        stk_close = data['close_preadj'].iloc[-2001:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = (stk_ret.rolling(1200, min_periods=600).corr(index_ret.iloc[:,0])).iloc[-800:]
        
        stk_index_corr = (stk_index_corr.replace([-np.inf, np.inf], np.nan))
        stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        bool_df = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        
        hclose = data['close_preadj'].iloc[-830:].values
        hopen = data['open_preadj'].iloc[-830:].values
        
        hlow = data['low_preadj'].iloc[-830:].values
        hhigh = data['high_preadj'].iloc[-830:].values
        
        temp = np.abs(hclose-hopen)
        temp[temp==0] = 0.01
        
        temp0 = (hhigh - hlow)
        temp1 = (temp0/temp)[-800:]
        a = bk.move_sum((hclose[1:]/hclose[:-1]-1), 30, min_count = 15, axis = 0)[-800:]
        vwtc_r = (temp1*(a))
        vwtc_r = pd.DataFrame(vwtc_r, index = bool_df.index, columns = bool_df.columns)

        factor = np.nanmean(vwtc_r[bool_df], axis = 1)
        
        factor = bk.move_mean(factor,10,  min_count = 5, axis = 0)
        #print(b.iloc[:, 0].corr(b1.iloc[:, 0]))
        factor2 = rolling_norm(factor, 242*3, method = 'ts_rank')
        factor2 = np.nanmean(factor2[-3:])

        return factor2