# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 17:02:37 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class CFG4_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'close_zz500']
        lookback_bars=2000
        super(CFG4_CC, self).__init__(required_columns=required_columns,
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

        hamount = df['amount_zz500']
        hclose = df['close_zz500']
        h_max = pd.Series([50]*len(hamount))
        h_max.index = hamount.index
        h_rank = hamount.stack(dropna=False).groupby(level=0).rank(ascending=False, method='first').unstack()
        selected = h_rank.le(h_max, axis=0)
        l_a = hamount[selected]
        l_a = l_a.fillna(0)
        f = (l_a*(hclose/hclose.shift(1)-1)).sum(axis = 1)/100
        f1 = f.rolling(60, min_periods = 5).mean()
        f1 = f1.to_frame()
        f2 = self.ts_rank(f1)
        f2.columns = [columnname]
        return f2