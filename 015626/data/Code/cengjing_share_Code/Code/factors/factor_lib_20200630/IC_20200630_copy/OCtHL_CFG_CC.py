# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 10:40:21 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class OCtHL_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'open_zz500', 'high_zz500', 'amount_zz500', 'weight_boolean_zz500']

        super(OCtHL_CFG_CC, self).__init__(required_columns=required_columns
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
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        temp1 = data['open_zz500'] - data['close_zz500']
        temp2 = data['high_zz500'] - data['low_zz500']
        t_pcor2 = -temp1/temp2
        t_pcor2[t_pcor2 == np.inf] = 0
        t_pcor2 = t_pcor2.rolling(45, min_periods = 15).mean()#.rolling(5, min_periods = 2).mean()
        factor = (t_pcor2*stk_amount).mean(axis = 1).to_frame()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor, 1000)
        return factor