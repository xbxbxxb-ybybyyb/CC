# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:55:42 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

def normalization(signal, holding_window = 1200): 
    max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
    min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
    a = (signal - min_s)/(max_s-min_s)
    a = 2*a-1
    aa = pd.DataFrame(a)
    aa.index = signal.index
    aa.columns = signal.columns
    return aa

class VwRetSk_CC(FactorGenerator):
    def __init__(self):
        
        required_columns =['vwap', 'recent_month_mask']

        super(VwRetSk_CC, self).__init__(
                                  required_columns=required_columns
                                  )
    def on_bar(self, data):

        vsk_r = -data['vwap'].diff().rolling(30, min_periods = 15).skew()       
        factor = (vsk_r[data['recent_month_mask']]).mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = normalization(factor)
        factor[factor<=-0.5] = 0
        return factor