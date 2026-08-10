# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 16:57:39 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex


class CFG15_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'close_spot', 'weight_zz500']
        lookback_bars=2000
        super(CFG15_CC, self).__init__(required_columns=required_columns,
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
        weight = df['weight_zz500']
        hret = hclose/hclose.shift(1) - 1
        a = hret.shift(1).rolling(1200, min_periods = 600).std()
        b = df['close_spot'].rolling(1200, min_periods = 600).std()
        a[abs(a)<1e-8] = np.nan
        b[abs(b)<1e-8] = np.nan
        c = (hret.shift(1)).rolling(1200, min_periods = 600).cov((df['close_spot']))
        temproll = c / (a.mul(b, axis=0))

        # temproll = (hret.shift(1)).rolling(1200, min_periods = 600).corr((df['close_spot']))

        corr_max = pd.Series([100]*len(temproll))
    
        corr_max.index = temproll.index
    
        corr_rank = temproll.stack(dropna=False).groupby(level=0).rank(ascending=False, method='first').unstack()
    
        selected_corr = corr_rank.le(corr_max, axis=0)
    
        corr_l = temproll[selected_corr]
    
        corr_l = corr_l.fillna(0)
        g = (weight * hret * ((corr_l > 0).astype(int))).sum(axis = 1)
        
        g1 = g.rolling(45, min_periods = 25).mean()
        g1 = g1.to_frame()
        g2 = self.ts_rank(g1)
        g2.columns = [columnname]  
        g2[g2<=-0.5] = np.nan
        return g2