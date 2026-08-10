# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:56:54 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


class HL123_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['low_if', 'high_if','recent_month_mask']

        super(HL123_CC_IF, self).__init__(required_columns=required_columns)
    
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
        hlow = df['low_if']
        hhigh = df['high_if']
        i11 = hhigh.rolling(10, min_periods = 5).max()-hlow.rolling(60, min_periods = 10).min()
        i12 = (hhigh.shift(30)).rolling(10, min_periods = 5).max()-(hlow.shift(30)).rolling(60, min_periods = 10).min()
        i2 = (i11-i12).rolling(20, min_periods = 2).mean()
        i2 = self.ts_rank(i2[df['recent_month_mask']].mean(axis = 1).to_frame())
        #i2 = self.normalization(i2)
        i2[i2>1] = 0
        i2[i2<=-0.5] = 0
        i2.columns = [columnname]    
        return i2