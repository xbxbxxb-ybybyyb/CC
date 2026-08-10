# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 09:08:07 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator import FactorGenerator
import numpy as np

class DJX_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns =['close_spot']

        super(DJX_ind_CC, self).__init__(
                                  required_columns=required_columns)
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
    
    def on_bar(self, data):

        temp5 = data['close_spot'].rolling(5, min_periods = 2).mean()
        temp10 = data['close_spot'].rolling(10, min_periods = 5).mean()
        temp20 = data['close_spot'].rolling(20, min_periods = 10).mean()
        temp60 = data['close_spot'].rolling(60, min_periods = 30).mean()
        temp120 = data['close_spot'].rolling(120, min_periods = 60).mean()
        temp5_diff = (temp5.diff()>0).astype(int)
        temp10_diff = (temp10.diff()>0).astype(int)
        temp20_diff = (temp20.diff()>0).astype(int)
        temp60_diff = (temp60.diff()>0).astype(int)
        temp120_diff = (temp120.diff()>0).astype(int)
        temp = (temp5_diff+temp10_diff+temp20_diff+temp60_diff+temp120_diff).rolling(15, min_periods = 5).mean()
        factor = self.ts_rank(temp.to_frame())
        # factor[factor<-0.5] = 0
        factor.columns = [self.__class__.__name__]
        return factor