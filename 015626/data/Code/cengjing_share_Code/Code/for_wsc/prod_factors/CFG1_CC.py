# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 17:00:25 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class CFG1_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'weight_zz500']
        lookback_bars=2000
        super(CFG1_CC, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)
    
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
        
        hclose = df['close_zz500']
        weight = df['weight_zz500']
        hret = (hclose/hclose.shift(1)-1)
        temp_weighted = hret*weight
        a = (temp_weighted.sum(axis = 1))
        a = a.to_frame()
        a.index.name = 'dt'
        a1 = a.rolling(90, min_periods = 15).mean()
        a2 = self.ts_rank(a1)
        a2.iloc[:, 0] = a2.iloc[:, 0].rolling(3, min_periods = 2).mean()
        a2.columns = [columnname]
        return a2