# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 17:08:29 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class CFG13_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'low_zz500', 'high_zz500']
        lookback_bars=2000
        super(CFG13_CC, self).__init__(required_columns=required_columns,
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
        hlow = df['low_zz500']
        hhigh = df['high_zz500']
        
        rol_range = (hhigh.rolling(30, min_periods = 10).max() - hlow.rolling(30, min_periods = 10).min())
        hhigh = (hhigh.rolling(30, min_periods = 10).max() - hclose)/rol_range 
        llow = (hclose - hlow.rolling(30, min_periods = 10).min())/rol_range
        i1 = llow.rolling(10, min_periods = 5).mean()-hhigh.rolling(10, min_periods = 5).mean()
        i2 = (i1).mean(axis = 1)
        i2 = self.ts_rank(i2.to_frame())
        i2[i2>1] = np.nan
        i2[i2<=-0.5] = np.nan
        i2.columns = [columnname]    
        return i2