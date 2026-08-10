# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 18:18:43 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class CFG18_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['high_zz500', 'close_zz500', 'weight_zz500', 'weight_boolean_zz500']

        super(CFG18_CC, self).__init__(required_columns=required_columns
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

    def on_bar(self, df):
        columnname = self.__class__.__name__
        hhigh = df['high_zz500']
        hclose = df['close_zz500']
        hweight = df['weight_zz500']
        hret = hclose/hclose.shift(1)-1
        #weight = df['weight_zz500'].xs('weight_zz500', axis=1, drop_level=True)
        htemp = (hhigh>=(hhigh.rolling(45, min_periods = 5).max())).astype(int).rolling(90, min_periods = 5).mean()
        htemp = ((hret*hweight)[df['weight_boolean_zz500']]).mean(axis = 1)
        htemp = self.ts_rank(htemp.to_frame().rolling(45, min_periods = 15).mean())
        #a2 = pd.DataFrame(a2)
        htemp.index = hhigh.index
        htemp.columns = [columnname]
        htemp[htemp<=-0.5] = 0
        return htemp