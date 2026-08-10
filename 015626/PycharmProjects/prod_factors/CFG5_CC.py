# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 17:03:14 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class CFG5_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['open_zz500', 'close_zz500', 'volume_zz500']
        lookback_bars=2000
        super(CFG5_CC, self).__init__(required_columns=required_columns,
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
        hopen = df['open_zz500']
        hclose = df['close_zz500']
        hvolume = df['volume_zz500']
        t1 = (hopen > hopen.shift(1)).astype(int)
        t2 = (hclose>hclose.shift(1)).astype(int)
        t3 = (hvolume>hvolume.shift(1)).astype(int)
        t = t1 + t2 + t3
        
        t = (t==3)
        aa = t.copy()
        aa2 = aa.rolling(30, min_periods = 15).mean()
        aa1 = aa2.mean(axis = 1).to_frame()
        aa2 = self.ts_rank(aa1)
        aa2[aa2<=-0.5] = np.nan
        aa2[aa2>1] = np.nan
        aa2.columns = [columnname]
        return aa2