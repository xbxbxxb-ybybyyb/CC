# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:08:45 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class HmaxC_ind_nr_al_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 2
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','high', 'adjfactor','turnover_rate', 'amount']
    normalize_size = 242# normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        df_s = data['amount'].iloc[-60:].sum()
        
        turnover = (data['turnover_rate'].iloc[-60:].mean())
        temp1 = df_s.gt(df_s.quantile(0.80))
        temp4 = turnover.gt(turnover.quantile(0.80))
        bool_df = (temp1&temp4).values.astype(float)
        bool_df[bool_df==0] = np.nan
        hhigh = data['high_preadj'].iloc[-370:].values
        hclose = data['close_preadj'].iloc[-243:].values
        hmhm_r = -bk.move_max(hhigh, 120, min_count = 90, axis = 0)[-243:]/hclose
        hmhm_r = rolling_norm(hmhm_r, 242)[-1]
        factor = np.nanmean(hmhm_r*bool_df)
        return factor