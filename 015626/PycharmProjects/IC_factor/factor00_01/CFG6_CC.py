# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 17:03:58 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class CFG6_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'turnover_zz500']
        lookback_bars=2000
        super(CFG6_CC, self).__init__(required_columns=required_columns,
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
        to = df['turnover_zz500']
        hclose = df['close_zz500']
        bb = to.rolling(25, min_periods = 15).mean()
        bbb = np.sign(hclose/hclose.shift(24)-1)*bb
        bb1= bbb.mean(axis = 1).to_frame()
        bb1 = bb1.rolling(10, min_periods = 5).mean()
        bb2 = self.ts_rank(bb1, 2420)
        bb2[bb2<=-0.5] = np.nan
        bb2[bb2>1] = np.nan
        bb2.columns = [columnname]
        return bb2