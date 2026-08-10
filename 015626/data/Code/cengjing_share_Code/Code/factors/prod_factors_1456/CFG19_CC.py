# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 10:16:52 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class CFG19_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'weight_zz500', 'weight_boolean_zz500']

        super(CFG19_CC, self).__init__(required_columns=required_columns
                                  )
    
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
    
    def to_ts(self, df, ret, weight, LS = True, Lag = False):
        ret = ret*weight
        #df = df.fillna(0)
        #print((df!=0).astype(int).sum(axis = 1))
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
        hweight = df['weight_zz500']
        hlow = df['low_zz500']
        hclose = df['close_zz500']
        hret = hclose/hclose.shift(1)-1
        #weight = df['weight_zz500'].xs('weight_zz500', axis=1, drop_level=True)
        htemp = (hlow<=(hlow.rolling(15, min_periods = 2).min())).astype(int).rolling(90, min_periods = 5).mean()
        htemp = self.to_ts(htemp, hret, hweight)
        htemp = self.normalization(htemp.to_frame().rolling(120, min_periods = 15).mean(), 242*3)
        #a2 = pd.DataFrame(a2)
        htemp.index = hlow.index
        htemp.columns = [columnname]
        htemp[htemp<=-0.5] = 0
        return htemp
