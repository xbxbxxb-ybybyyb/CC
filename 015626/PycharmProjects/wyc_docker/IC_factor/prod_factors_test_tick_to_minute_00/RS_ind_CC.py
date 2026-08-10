# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 17:50:07 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator


class RS_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']

        super(RS_ind_CC, self).__init__(required_columns=required_columns)
        
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
        columnname = self.__class__.__name__
        ret = data['close_spot']/data['close_spot'].shift(1)-1
        a = ret.rolling(25, min_periods = 15).std()
        a[abs(a)<1e-8] = np.nan
        i1 = (data['close_spot']/data['close_spot'].shift(24)-1) / a
        i1 = i1.to_frame()
        i2 = self.normalization(i1.rolling(8, min_periods = 2).mean(), 242)
        #i2 = self.normalization(i2)
        i2[i2>1] = np.nan
        i2[i2<=-0.5] = np.nan
        i2.columns = [columnname]    
        return i2