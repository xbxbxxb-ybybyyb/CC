# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:55:46 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *




class LCCorr_nr_a3_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'amount', 'low']
    normalize_size = 2400 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hamount = data['amount'].iloc[-136:]
        df_s = (hamount.rolling(120, min_periods = 15).sum())
        hclose = data['close_preadj'].iloc[-50:]
        
        ret = (hclose/hclose.shift(30)-1)
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0).values[-15:]
        temp6 = ret.gt(pd.Series(ret.quantile(0.80, axis = 1)), axis=0).values[-15:]    
        mask = temp1*temp6
        
        high = data['low_preadj'].iloc[-1322:]
        close = data['close_preadj'].iloc[-1322:]
        s = bk.move_std(high.values, 60, min_count = 30, axis = 0)
        f = bk.move_std(close.values, 60, min_count = 30, axis = 0)
        s[abs(s) < 1e-7] = np.nan
        f[abs(f) < 1e-7] = np.nan
        t_chgpcor2 = (high.rolling(60, min_periods=30).cov(close)).values / (s * f)
        t_chgpcor2 = rolling_norm(t_chgpcor2)[-15:]
        tempdf = np.nansum(t_chgpcor2*mask, axis = 1)
        factor = np.nanmean(tempdf)
        
        return factor