# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:47:17 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

  
class BS_Main_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount','BuyUniqueOrderNum','BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-25:]
        df_s = amount.rolling(10, min_periods = 5).sum()
        
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0).astype(float).values
        bool_df[bool_df==0] = np.nan
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-25:]
        BuyTradeNum = data['BuyTradeNum'].values[-25:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-25:]
        SellTradeNum = data['SellTradeNum'].values[-25:]
        
        factor = BuyUniqueOrderNum/BuyTradeNum - SellUniqueOrderNum/SellTradeNum


        factor = np.nanmean(np.nanmean(factor * bool_df, axis = 1)[-6:])

        return -factor