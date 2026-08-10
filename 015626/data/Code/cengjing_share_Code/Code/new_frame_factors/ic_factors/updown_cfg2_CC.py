# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:06:51 2021

@author: appadmin
"""


import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


#
class updown_cfg2_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['amount', 'close','adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-215:]        
        df_s = (amount.rolling(120, min_periods = 15).sum())
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0).astype(float)
        stk_amount[stk_amount==0] = np.nan
        hclose_o = data['close_preadj'].iloc[-216:].values
        
        hclose = (hclose_o[1:]/hclose_o[:-1]-1)
        upclose = np.nansum(stk_amount*((hclose>0).astype(int)), axis = 1)
        downclose = np.nansum(stk_amount*((hclose<0).astype(int)), axis = 1)

        vwtc_r = np.nanmean(((upclose-downclose)/ (upclose+downclose))[-90:], axis = 0)
        if abs(vwtc_r)>10000:
            vwtc_r = np.nan
        
        return vwtc_r