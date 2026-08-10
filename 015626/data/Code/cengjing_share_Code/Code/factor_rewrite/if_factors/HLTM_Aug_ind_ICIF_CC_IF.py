# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:44:07 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

class HLTM_Aug_ind_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'volume']}
    normalize_size = 5 * 242
    normalize_type = 'ts_rank'
    #num_range = '[-0, 1]'
    
    def calculate(self, data):
        hlow = (data['low_000905.SH'].values)[-90:]
        hhigh = (data['high_000905.SH'].values)[-90:]
        hclose = (data['close_000905.SH'].values)[-90:]
        hvolume = (data['volume_000905.SH'].values)[-90:]
        
        temp1 = bk.move_max(hhigh, 15, min_count = 7) - hclose
        
        #temp2 = data['close_spot']-data['low_spot'].rolling(15, min_periods = 7).min()
        temp2 = hclose - bk.move_min(hlow, 15, min_count = 7)
        
        temp = np.where(temp1>temp2, temp1, temp2)

        factor = np.nanmean((temp*hvolume)[-35:])
        return factor
    