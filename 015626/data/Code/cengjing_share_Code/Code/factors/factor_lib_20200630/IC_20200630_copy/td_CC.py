# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 17:09:20 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator

# 多头因子
class td_CC(FactorGenerator):
    def __init__(self):
        required_columns =['low', 'high', 'recent_month_mask']
        
        super(td_CC, self).__init__(
                                  required_columns=required_columns)

    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    

    def on_bar(self, data):
        temp = data['low'].rolling(10, min_periods = 5).min()-data['low'].rolling(60, min_periods = 5).min()+data['high'].rolling(10, min_periods = 5).max()-data['high'].rolling(60, min_periods = 5).max()
        factor = (temp[data['recent_month_mask']]).mean(axis= 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor)
        factor[factor<=-0.5] = 0
        factor[factor>1] = 0
        return factor
