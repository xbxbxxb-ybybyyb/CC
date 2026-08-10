# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:58:05 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class HDLD_CFG_CC_IH(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'open', 'adjfactor', 'amount']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-120:]
        df_s = amount.sum(axis = 0)
        bool_df = df_s.gt((df_s.quantile(0.90))).values.astype(float)
        bool_df[bool_df==0] = np.nan
        hopen = data['open_preadj'].iloc[-65:].values
        hclose = data['close_preadj'].iloc[-65:].values
        temp1 = np.where(hopen>hclose, hopen, hclose)
        temp2 = np.where(hopen>hclose, hclose, hopen)
        
        t_pcorr = np.nanmean(((temp1[1:] - temp1[:-1])+(temp2[1:] - temp2[:-1]))[-60:], axis = 0)
        
        factor = np.nanmean(t_pcorr*bool_df)

        return factor