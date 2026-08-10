# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:55:29 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *




class HL123_nr_av_CC_CFG_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor', 'high','close','amount', 'low']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hamount = data['amount'].iloc[-150:]
        df_s = hamount.rolling(120, min_periods = 15).sum()
        stk_close = data['close_preadj'].iloc[-61:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0).values[-30:]
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0).values[-30:]
        mask = (temp3*temp1)

        hlow = data['low_preadj'].iloc[-1330:]
        hhigh = data['high_preadj'].iloc[-1330:]

        hlow_s = hlow.shift(30).values
        hhigh_s = hhigh.shift(30).values

        hlow = hlow.values
        hhigh = hhigh.values

        i11 = bk.move_max(hhigh, 10, min_count = 5, axis = 0)-bk.move_min(hlow, 60, min_count = 10, axis = 0)
        i12 = bk.move_max(hhigh_s, 10, min_count = 5, axis = 0)-bk.move_min(hlow_s, 60, min_count = 10, axis = 0)
        i2 = (i11-i12)
        i2 = rolling_norm(i2, 242*5)[-30:]
        
        factor = np.nanmean(np.nansum(i2*mask, axis = 1))
        return factor