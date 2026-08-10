# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:05:16 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



#
class cmh_ae_CFG_CC_IM(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','amount', 'low', 'high', 'turnover_rate', 'adjfactor']
    normalize_size = 242 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀

    def calculate(self, data):
        
        turnover = data['turnover_rate'].iloc[-46:]
        amount = data['amount'].iloc[-131:]
        
        df_s = (amount.rolling(120, min_periods = 15).sum())
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0).iloc[-10:].values
        ret_30 = (turnover/turnover.shift(30)-1)
        ret_30 = ret_30.replace([-np.inf, np.inf], np.nan)
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0).iloc[-10:].values

        bool_df = (temp1&temp5)
        
        hhigh = data['high_preadj'].iloc[-1335:].values  
        hclose = data['close_preadj'].iloc[-1335:].values 
        
        vwtc_r = (hhigh-bk.move_mean(hclose, 120, min_count = 30, axis = 0))
        vr = rolling_norm(vwtc_r)[-10:]
        
        factor = np.nanmean(vr*bool_df, axis = 0)
        factor = np.nanmean(factor)
               
        return factor