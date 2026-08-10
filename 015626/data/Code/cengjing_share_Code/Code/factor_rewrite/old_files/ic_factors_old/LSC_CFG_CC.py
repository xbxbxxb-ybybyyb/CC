# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:01:57 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class LSC_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 8
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','low', 'high', 'adjfactor', 'amount']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        amount = data['amount'].iloc[-125:]
        df_s = amount.rolling(120, min_periods = 15).sum()
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0).iloc[-3:].values
        
        
        index_close = data['close_000905.SH'].iloc[-1206:]
        stk_close = data['close_preadj'].iloc[-1206:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = (stk_ret.iloc[-1204:].rolling(1200, min_periods=1200).corr(index_ret.iloc[-1204:,0])).iloc[-3:]
        
        stk_index_corr = (stk_index_corr.replace([-np.inf, np.inf], np.nan)).values
        bool_df = (stk_index_corr*stk_amount)
        
        hhigh = data['high_preadj'].values[-55:]
        hclose = data['close_preadj'].values[-55:]
        hlow = data['low_preadj'].values[-55:]
        
        h = bk.move_max(hhigh, 30, min_count = 10, axis = 0)
        l = bk.move_min(hlow, 30, min_count = 10, axis = 0)
        hld = h - l
        
        hh = (h-hclose)/(hld)
        ll = (hclose-l)/(hld)
        
        hh[abs(hh)>100000] = np.nan
        ll[abs(ll)>100000] = np.nan
        
        vwtc_r = (bk.move_mean(ll, 15, min_count = 5, axis = 0) - bk.move_mean(hh, 15, min_count = 5, axis = 0))[-3:]
        factor = np.nanmean(vwtc_r*bool_df, axis = 1)
        factor = np.nanmean(factor)
        return factor