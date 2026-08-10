# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 13:27:19 2021

@author: appadmin
"""


import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class Short_BS9_2_CC_IF_IM(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_superorder_count', 'buy_bigorder_count', 'buy_midorder_count',  'buy_smallorder_count']
    normalize_size = 1200
    normalize_type = 'ts_rank' 

    handle_preadj = False
    
    def calculate(self, data):
        
        a = data['buy_superorder_count'][-3:].fillna(0) + data['buy_bigorder_count'][-3:].fillna(0) + data['buy_midorder_count'][-3:].fillna(0) + data['buy_smallorder_count'][-3:].fillna(0)
        temp2 = (data['buy_bigorder_count'][-3:].fillna(0) + data['buy_superorder_count'][-3:].fillna(0))/ a.replace(0, np.nan)
        temp2 = temp2.replace([-np.inf, np.inf], np.nan)
        factor = np.nanmean(temp2.values,axis = 1)
        factor = np.nanmean(factor)
        
        return factor