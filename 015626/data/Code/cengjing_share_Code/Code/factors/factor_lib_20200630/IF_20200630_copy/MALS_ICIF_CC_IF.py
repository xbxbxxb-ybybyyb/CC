# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 13:46:35 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


class MALS_ICIF_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['low_spot']
        super(MALS_ICIF_CC_IF, self).__init__(required_columns=required_columns)
        
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

        temp = data['low_spot'].rolling(75, min_periods = 15).mean() - data['low_spot'].shift(15).rolling(60, min_periods = 7).mean()
        factor = temp.to_frame()
        factor = self.ts_rank(factor, 242*2)
        factor[factor<-0.5] = 0
        factor.columns = [self.__class__.__name__]
        return factor