# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:58:25 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



class cd_ind_nr_at_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'amount']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-75:]
        hamount = data['amount'].iloc[-135:]
        
        temp = bk.move_mean(tover, 60, min_count = 15, axis = 0)
        tempp = bk.move_sum(hamount, 120, min_count = 15, axis = 0)
        turnover = pd.DataFrame(temp,index = tover.index, columns = tover.columns).iloc[-10:]
        df_s = pd.DataFrame(tempp,index = hamount.index, columns = hamount.columns).iloc[-10:]
        
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)

        mask = temp1*temp4
        
        hclose = data['close_preadj'].iloc[-1280:].values
        
        hmean = bk.move_mean(hclose, 60, min_count = 2, axis = 0)
        htemp = hmean[1:] - hmean[:-1]
        
        htemp = rolling_norm(htemp, 242*5)[-10:]
        tempdf = np.nansum(htemp*mask, axis = 1)
        factor = np.nanmean(tempdf)
        return factor