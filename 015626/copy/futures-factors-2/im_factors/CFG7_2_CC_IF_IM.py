# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:51:49 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class CFG7_2_CC_IF_IM(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','open', 'weight','close','turnover_rate']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        to = data['turnover_rate'].iloc[-180:].values
        hclose = data['close_preadj'].iloc[-181:].values
        hopen = data['open_preadj'].iloc[-181:].values
        
        df_s = data['weight'].iloc[-181:]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0).values.astype(float)[-180:]
        bool_df[bool_df == 0] = np.nan
        
        ret = (hclose/hopen -1)[-180:]
        hret = hclose[1:]/hclose[:-1] -1
        
        ret[abs(ret)>100000] = np.nan
        hret[abs(hret)>100000] = np.nan
        
        a = (hclose<hopen).astype(float)[-180:]
        
        cc1 = (((to*a)/abs(ret*a)))
        cc1[abs(cc1) > 100000] = np.nan
        ccc1 = bk.move_mean(cc1, 90, min_count = 7, axis = 0)
        ccc1 = ccc1*bool_df
        hret = hret*bool_df
        ccc1 = pd.DataFrame(ccc1, index = data['close_preadj'].iloc[-180:].index, columns = data['close_preadj'].iloc[-180:].columns)
        hret = pd.DataFrame(hret, index = data['close_preadj'].iloc[-180:].index, columns = data['close_preadj'].iloc[-180:].columns)
        cc2 = to_ts(ccc1, hret).values
        ccc2 = np.nanmean(cc2[-90:])
        
        return ccc2
   