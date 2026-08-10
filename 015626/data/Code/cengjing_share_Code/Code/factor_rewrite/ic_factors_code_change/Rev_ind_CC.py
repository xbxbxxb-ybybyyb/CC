# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:32:48 2021

@author: appadmin
"""


import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class Rev_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}  
    normalize_size = 4800
    normalize_type = 'rolling_norm'
    num_range = '[-1, 1]'
    
    def calculate(self, data):
        hclose = data['close_000905.SH'].iloc[-150:]
        ret = (hclose.iloc[-1]/hclose.shift(120).iloc[-1]-1)

        return ret
    