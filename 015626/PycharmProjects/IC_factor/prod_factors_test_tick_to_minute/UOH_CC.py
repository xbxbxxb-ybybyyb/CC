# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 14:16:10 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex


class UOH_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['high_zz500', 'open_zz500']
        lookback_bars=2000
        super(UOH_CC, self).__init__(required_columns=required_columns,
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
            

    def on_bar(self, data):
        
        upopentohigh = (data['open_zz500']-data['high_zz500'].shift(1)>0).sum(axis = 1)
        temp1 = upopentohigh.rolling(30, min_periods = 15).mean().rolling(5, min_periods = 2).mean()
        #temp2 = data['downopentolow'].rolling(30, min_periods = 15).mean()
        t_pcorr = temp1
        factor = t_pcorr.to_frame()
        factor.index = data['open_zz500'].index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        factor[factor>1] = np.nan
        factor[factor<0] = np.nan
        #factor[factor == np.nan] = 0
        return factor
