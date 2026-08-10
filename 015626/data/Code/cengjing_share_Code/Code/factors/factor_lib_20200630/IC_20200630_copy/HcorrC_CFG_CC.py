# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 13:34:01 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class HcorrC_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_zz500', 'close_zz500', 'high_zz500', 'weight_boolean_zz500']

        super(HcorrC_CFG_CC, self).__init__(required_columns=required_columns
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
    def on_bar(self, data):

        high = data['high_zz500']
        close = data['close_zz500']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-7] = np.nan
        f[abs(f) < 1e-7] = np.nan
        t_pcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)

        t_pcor2[~np.isfinite(t_pcor2)] = 0
        factor = (t_pcor2[data['weight_boolean_zz500']]*data['weight_zz500']).mean(axis = 1).to_frame()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor