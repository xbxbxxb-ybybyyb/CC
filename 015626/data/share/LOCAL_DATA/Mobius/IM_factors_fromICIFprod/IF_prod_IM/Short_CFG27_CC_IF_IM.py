# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 17:44:21 2021

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import *
from future_factor import FutureFactor


class Short_CFG27_CC_IF_IM(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['volume', 'low', 'high', 'close']
    normalize_size = 10*240
    normalize_type = 'ts_rank' 

    handle_preadj = False
    
    def calculate(self, data):
        
        hclose = data['close'].values[-188:]
        hhigh = data['high'].values[-188:]
        hlow = data['low'].values[-188:]
        hvolume = data['volume'].values[-188:]
        
        hret = (hclose[1:]/hclose[:-1] - 1)[-36:]
        temp1 = bk.move_max(hhigh, 90, 7, axis = 0)-hclose
        temp2 = hclose-bk.move_min(hlow, 90, 7, axis = 0)
        
        temp11 = (temp1>temp2)
        temp22 = (temp2>=temp1)

        temp = temp11*temp1 + temp22*temp2
        i1 = bk.move_mean(temp*hvolume, 60, 2, axis = 0)[-36:]
        
        
        df_s_mask = np.nanmedian(i1, axis=1)
        

        df_s_mask = np.expand_dims(df_s_mask, axis=-1)

        hret_1 = ma.array(hret, mask=(i1<=df_s_mask))

        hret_2 = ma.array(hret, mask=(i1>=df_s_mask))
        
        temp2 = np.nanmean(hret_1, axis=1) - np.nanmean(hret_2, axis=1)
        factor = np.nanmean(temp2[-35:])
        
        return factor