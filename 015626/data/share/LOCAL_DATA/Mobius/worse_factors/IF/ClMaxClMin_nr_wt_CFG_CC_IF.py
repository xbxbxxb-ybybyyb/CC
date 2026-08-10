# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:52:41 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    
class ClMaxClMin_nr_wt_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close','turnover_rate', 'weight']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
         
        stk_weight = data['weight'].values[-66:]
        tover = data['turnover_rate'].iloc[-66:]
        turnover = tover.rolling(60, min_periods = 15).mean()
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values
        mask = (stk_weight*temp4)[-5:]
        
        hclose = data['close_preadj'].values[-1265:]
        m_vwap_ind_r = bk.move_max(hclose, 45, min_count = 30, axis = 0)/bk.move_min(hclose, 45, min_count = 30, axis = 0)
        m_vwap_ind_r[np.abs(m_vwap_ind_r)>10000] = np.nan
        temp = rolling_norm(m_vwap_ind_r, 242*5)[-5:]
        tempdf = np.nanmean(np.nansum(temp*mask, axis = 1))
        
        return tempdf