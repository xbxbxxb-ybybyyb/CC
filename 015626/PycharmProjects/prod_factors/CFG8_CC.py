# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 17:05:28 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class CFG8_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'volume_zz500', 'float_shares_zz500']
        lookback_bars=2000
        super(CFG8_CC, self).__init__(required_columns=required_columns,
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
        hvolume = df['volume_zz500']
        hclose = df['close_zz500']
        hfs = df['float_shares_zz500']
        hret = hclose/hclose.shift(1) - 1
        d1 = hvolume/hclose/hfs
        d1 = self.to_ts(d1, hret)
        dd1 = d1.rolling(30, min_periods = 15).mean()
        dd2 = self.normalization(dd1.to_frame())
        dd2.columns = [columnname]
        dd2[dd2<=-1] = np.nan
        dd2[dd2>1] = np.nan
        
        return dd2
