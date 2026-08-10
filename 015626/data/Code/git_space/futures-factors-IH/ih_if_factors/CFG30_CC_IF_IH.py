# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:51:30 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



class CFG30_CC_IF_IH(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','amount', 'close']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hclose = data['close_preadj'].iloc[-46:].values
        hamount = data['amount'].iloc[-106:]
        
        df_s = hamount.rolling(60, min_periods = 15).sum()
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0).values[-45:].astype(float)
        bool_df[bool_df==0]=np.nan
        
        upclose = np.nansum(((hclose[1:]*bool_df)>(hclose[:-1]*bool_df)), axis = 1)
        downclose = np.nansum(((hclose[1:]*bool_df)<(hclose[:-1]*bool_df)), axis = 1)
        t_prcd2 = (upclose-downclose)/ (upclose+downclose)
        
        t_prcd2[abs(t_prcd2)>1000000] = np.nan
        
        factor = np.nanmean(t_prcd2)
        return factor