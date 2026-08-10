# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 09:08:13 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class updown_cfg3_CC(FactorGeneratorComplex):
    def __init__(self):

        required_columns =['close_zz500']

        super(updown_cfg3_CC, self).__init__(
                                  required_columns=required_columns
                                 )
        
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
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

    def on_bar(self, data):
        hc = data['close_zz500']/data['close_zz500'].shift(1)-1
        upclose = (hc>0).sum(axis = 1)
        downclose = (hc<0).sum(axis = 1)
        a = (upclose+downclose).rolling(30, min_periods = 15).mean()
        a[abs(a) < 1e-8] = np.nan
        vwtc_r = upclose.rolling(30, min_periods = 15).mean()/a
        factor = (vwtc_r.rolling(10, min_periods = 2).mean()).to_frame()
        factor.index = hc.index
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor, 960)
        factor[factor<=-0.5] = np.nan
        return factor