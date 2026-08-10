# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:07:33 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class updown_cfg4_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','volume', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hclose_o = data['close_preadj'].iloc[-36:].values
        hvolume_o = data['volume_preadj'].iloc[-36:].values
        
        hc = (hclose_o[1:]/hclose_o[:-1]-1)
        hcv = (hvolume_o[1:]/hvolume_o[:-1]-1)
        upclose = np.nansum((hc>0).astype(int), axis = 1)
        downclose = np.nansum((hc<0).astype(int), axis = 1)
        upvolume = np.nansum((hcv>0).astype(int), axis = 1)
        downvolume = np.nansum((hcv<0).astype(int), axis = 1)
        
        aa = (upclose/downclose)
        aa[abs(aa)>100000] = np.nan
        bb = (upvolume/downvolume)
        bb[abs(bb)>100000] = np.nan
        vwtc_r = (aa/bb)
        vwtc_r[abs(vwtc_r)>100000] = np.nan
        factor = np.nanmean(vwtc_r)
        return factor