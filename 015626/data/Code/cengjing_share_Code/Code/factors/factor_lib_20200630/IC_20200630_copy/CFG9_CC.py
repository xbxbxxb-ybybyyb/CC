# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 14:04:15 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class CFG9_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'weight_boolean_zz500']

        super(CFG9_CC, self).__init__(required_columns=required_columns
                                  )
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
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def to_ts(self, df, ret, LS = True, Lag = False):
        if LS == True:
            if Lag == False:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)-(df.lt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)
            else:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)-(df.lt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)
        else:
            if Lag == False:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)
            else:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)

    
    def on_bar(self, df):
        columnname = self.__class__.__name__

        hclose = df['close_zz500']
        hret = hclose/hclose.shift(1) - 1
        
        e = hclose.rolling(30, min_periods = 20).max()/hclose.rolling(30, min_periods = 20).min()
        e = e[df['weight_boolean_zz500']]
        hret = hret[df['weight_boolean_zz500']]
        e1 = self.to_ts(e, hret)
        ee1 = e1.rolling(30, min_periods = 15).mean()
        e2 = self.normalization(ee1.to_frame())
        e2[e2<=0] = 0
        e2[e2>1] = np.nan
        e2.columns = [columnname]
        #e2.iloc[:, 0] = e2.iloc[:, 0].rolling(3, min_periods = 2).mean()
        return e2
