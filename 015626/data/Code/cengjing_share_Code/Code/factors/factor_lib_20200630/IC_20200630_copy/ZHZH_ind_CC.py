# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 18:08:58 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator import FactorGenerator

class ZHZH_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot']

        super(ZHZH_ind_CC, self).__init__(
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

        temp = (data['high_spot']>=(data['high_spot'].rolling(15, min_periods = 5).max())).astype(int).rolling(60, min_periods = 5).mean()
        factor = self.ts_rank(temp.to_frame())
        factor.columns = [self.__class__.__name__]
        factor[factor<0] = 0
        return factor