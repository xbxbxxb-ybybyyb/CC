# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:52:24 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *




class CFG8_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','open', 'volume','close', 'float_shares']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hvolume = data['volume_preadj'].iloc[-45:].values
        hclose = data['close_preadj'].iloc[-46:].values
        hfs = data['float_shares'].iloc[-45:].values
        
        hret = hclose[1:]/hclose[:-1] - 1
        d1 = hvolume/(hclose[-45:])/hfs
        
        hret[abs(hret)>100000] = np.nan
        d1[abs(d1)>100000] = np.nan
        
        d1 = pd.DataFrame(d1, index = data['close_preadj'].iloc[-45:].index, columns = data['close_preadj'].iloc[-45:].columns)
        hret = pd.DataFrame(hret, index = data['close_preadj'].iloc[-45:].index, columns = data['close_preadj'].iloc[-45:].columns)
        d1 = to_ts(d1, hret).values
        ccc2 = np.nanmean(d1)
        
        return ccc2