# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:31:23 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class OCtHL_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':[ 'close','low','high', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = [-0.499999, 1]
    
    def calculate(self, data):

        hopen = (data['open_cont_IC'].values)[-40:]
        hclose = (data['close_cont_IC'].values)[-40:]
        hhigh = (data['high_cont_IC'].values)[-40:]
        hlow = (data['low_cont_IC'].values[-40:])
        temp1 = hopen - hclose
        temp2 = hhigh - hlow
        temp2[abs(temp2)<1e-8] = np.nan
        
        t_pcor2 = -temp1/temp2
        
        t_pcor2[abs(t_pcor2) > 1e8] = 0
        
        factor = bk.move_mean(bk.move_mean(t_pcor2, 30, min_count = 15),5, min_count = 2) 
        
        return factor[-1]
