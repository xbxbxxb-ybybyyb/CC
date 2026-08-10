# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 17:37:12 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class LSC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high', 'low', 'close', 'recent_month_mask']

        super(LSC_CC, self).__init__(
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
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
        
    def on_bar(self, data):

        hh = (data['high'].rolling(30, min_periods = 10).max() - data['close'])/(data['high'].rolling(30, min_periods = 10).max() - data['low'].rolling(30, min_periods = 10).min()) 
        ll = (data['close'] - data['low'].rolling(30, min_periods = 10).min())/(data['high'].rolling(30, min_periods = 10).max() - data['low'].rolling(30, min_periods = 10).min())
        vwtc_r = ll.rolling(20, min_periods = 15).mean()-hh.rolling(20, min_periods = 15).mean()
        factor = vwtc_r[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor, 242*4)
        factor[factor<=-0.5] = np.nan
        factor = factor.rolling(3, min_periods = 2).mean()
        factor = self.ts_rank(factor)
        factor[factor<0] = 0
        return factor


