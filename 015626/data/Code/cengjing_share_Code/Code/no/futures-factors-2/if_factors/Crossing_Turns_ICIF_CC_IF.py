# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:41:54 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *
      

# 先mask再rolling
class Crossing_Turns_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'open', 'high', 'low', 'vwap']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        
        hclose = (data['close_cont_IC'].values)[-1000:]
        hopen = (data['open_cont_IC'].values)[-1000:]
        hhigh = (data['high_cont_IC'].values)[-1000:]
        hlow = (data['low_cont_IC'].values)[-1000:]
        hvwap = (data['vwap_cont_IC'].values)[-1000:]
        
        temp = np.abs((np.where(hopen-hclose== 0, 0.1, hopen-hclose)))

        temp0 = hhigh - hlow

        temp1 = temp0/temp
        temp1[temp1>1000000] = np.nan
        temp1[temp1<-1000000] = np.nan
        shift_1 = shift(hvwap, 1)
        shift_1[shift_1==0] = np.nan
        a = bk.move_sum((hvwap/shift_1-1), 30, min_count = 15)
        vwtc_r = bk.move_mean(temp1*(a), 25, min_count = 5)

        factor = ts_rank(vwtc_r, 242*3)
        factor = np.nanmean(factor[-2:])
        if factor<=-0.5:
            factor = np.nan
            
        return factor