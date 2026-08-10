# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:32:29 2021

@author: appadmin
"""


import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class Rev_CC_IH(FutureFactor):
    
    data_type = 'Future'
    days_past = 11
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':[ 'close']}
    normalize_size = 2420
    normalize_type = 'rolling_norm'
#    num_range = '[-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        hclose = data['close_cont_IH'].iloc[-190:]
        ret = (hclose/hclose.shift(180)-1).values
        #print(shift(hclose, 180))
        factor = bk.move_mean(ret, 3, min_count = 2)
        #print(factor[-1])
        return factor[-1]
    