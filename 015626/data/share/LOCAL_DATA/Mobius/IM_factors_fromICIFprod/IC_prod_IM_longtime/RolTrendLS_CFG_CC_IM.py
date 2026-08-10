# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:03:03 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class RolTrendLS_CFG_CC_IM(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'low', 'high','open', 'amount', 'adjfactor']
    data_dict['Index_Id'] = {'000852.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        hhigh = data['high_preadj'].iloc[-145:].values
        hclose = data['close_preadj'].iloc[-145:].values
        hlow = data['low_preadj'].iloc[-145:].values
        
        amount = data['amount'].iloc[-127:]
        df_s = amount.rolling(120, min_periods = 15).sum()
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0).iloc[-5:]

        index_close = data['close_000852.SH'].iloc[-1208:]
        stk_close = data['close_preadj'].iloc[-1208:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = (stk_ret.iloc[-1206:].rolling(1200, min_periods=1100).corr(index_ret.iloc[-1206:,0])).iloc[-5:]
        stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        
        stk_index_corr = (stk_index_corr.replace([-np.inf, np.inf], np.nan))
        bool_df = (stk_index_corr*stk_amount).astype(float)
        bool_df[bool_df==0] = np.nan
        
        l = bk.move_min(hlow, 120, min_count = 15, axis = 0)
        h = bk.move_max(hhigh, 120, min_count = 15, axis = 0)
        
        a = h - l
        a[abs(a)<1e-8] = np.nan
        
        ll = (hclose - l) / a
        a2 = bk.move_mean(ll, 10, min_count = 5, axis = 0)
        a3 = bk.move_mean(a2, 10, min_count = 5, axis = 0)
        vwtc_r = (3*a3-2*a2)[-5:]

        factor = np.nanmean(vwtc_r*bool_df, axis = 1)
        factor = np.nanmean(factor)
        
        return factor 