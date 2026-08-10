# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 10:15:11 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from operators_cc import *
import pandas as pd

class hhll_ind_CC_nr_ct_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','turnover_rate','low', 'high', 'stk_index_corr_zz500', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-100:]       
        turnover = (tover.rolling(60, min_periods = 15).mean())[-31:]
        stk_index_corr = data['stk_index_corr_zz500'].iloc[-31:]        
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        tempp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0).values
        tempp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values
        
        hhigh = data['high_preadj'].iloc[-1235:].values
        hlow = data['low_preadj'].iloc[-1235:].values
        
        d1 = (hhigh[1:]>hhigh[:-1])
        d2 = (hlow[1:]>hlow[:-1])
        
        d_f = (d1.astype(int)+d2.astype(int))
        d_f[d_f == 2] = 4
        
        factor1 = rolling_norm(d_f)[-31:]
        
        mask = (tempp2 * tempp4)
        factor = np.nansum(factor1*mask, axis = 1)
        
        factor = np.nanmean(factor[-30:])
        return factor