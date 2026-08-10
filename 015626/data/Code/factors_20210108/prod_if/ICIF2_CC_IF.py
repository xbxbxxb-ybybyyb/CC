# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 10:31:33 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
import bottleneck as bk

class ICIF2_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']

        super(ICIF2_CC_IF, self).__init__(required_columns=required_columns)
        
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
        
    def on_bar(self, data):
        columnname = self.__class__.__name__
        ret = data['close_spot']/data['close_spot'].shift(1)-1
        i1 = (data['close_spot']/data['close_spot'].shift(24)-1) / ret.rolling(25, min_periods = 15).std()
        i1 = i1.to_frame()
        i2 = self.ts_rank(i1.rolling(20, min_periods = 2).mean())
        i2[i2>1] = 0
        i2[i2<=-0.5] = 0
        i2.columns = [columnname]    
        return i2