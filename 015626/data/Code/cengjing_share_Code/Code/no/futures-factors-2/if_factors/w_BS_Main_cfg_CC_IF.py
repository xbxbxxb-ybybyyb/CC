# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:58:53 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

def ts_mean(data, d):
    # moving time-series mean for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_mean(data, window=d, min_count=int(d / 2), axis=0)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_mean(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_mean(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
    return output

class w_BS_Main_cfg_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'weight', 'BuyUniqueOrderNum', 'BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 900 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        hclose = ts_mean(data['close'].iloc[-7:], 6)
        hret = (hclose/hclose.shift(1) - 1).iloc[-1]
        hret_mask = ((hret > 0).values * data['weight'].values[-1])
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-1]
        stk_BuyTradeNum = data['BuyTradeNum'].values[-1]
        stk_SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-1]
        stk_SellTradeNum = data['SellTradeNum'].values[-1]        
        factor_raw = (stk_BuyUniqueOrderNum / r(stk_BuyTradeNum)) - (stk_SellUniqueOrderNum / r(stk_SellTradeNum))
        factor = -np.nanmean(factor_raw * hret_mask)
        return factor