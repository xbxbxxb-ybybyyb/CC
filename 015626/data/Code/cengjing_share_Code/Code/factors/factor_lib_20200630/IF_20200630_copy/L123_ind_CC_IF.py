# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:28:58 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


class L123_ind_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['low_spot_if']

        super(L123_ind_CC_IF, self).__init__(required_columns=required_columns)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low_spot_if']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12).rolling(60, min_periods = 2).mean()
        i2 = self.ts_rank(i2.to_frame())
        i2.columns = [columnname]    
        return i2