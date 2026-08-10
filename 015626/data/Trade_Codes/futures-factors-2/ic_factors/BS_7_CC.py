# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:48:00 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class BS_7_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_superorder_money', 'buy_bigorder_money', 'amount']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-65:]
        df_s = amount.rolling(60, min_periods = 5).sum()
        bool_df = (df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)).values.astype(float)
        bool_df[bool_df==0] = np.nan
        
        buy_superorder_money_500 = data['buy_superorder_money'].fillna(0).values[-65:]
        buy_bigorder_money_500 = data['buy_bigorder_money'].fillna(0).values[-65:]
        amount = data['amount'].values[-65:]
        factor = (buy_superorder_money_500+buy_bigorder_money_500)/amount
        
        factor[abs(factor)>100000] = np.nan

        factor = np.nanmean(factor[-15:], axis = 0)
        factor = np.nanmean(factor*bool_df[-1])
            
        return np.nanmean(factor)