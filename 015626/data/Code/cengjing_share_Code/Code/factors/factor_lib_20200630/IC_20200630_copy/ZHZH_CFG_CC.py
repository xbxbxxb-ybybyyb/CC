# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:51:35 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class ZHZH_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'high_zz500', 'weight_boolean_zz500']
        
        super(ZHZH_CFG_CC, self).__init__(required_columns=required_columns
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
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        temp = (data['high_zz500']>=(data['high_zz500'].rolling(30, min_periods = 5).max())).astype(int).rolling(40, min_periods = 5).mean()
        temp = (temp[bool_df]).mean(axis = 1)
        factor = self.ts_rank(temp.to_frame())
        #factor = self.ts_rank(factor)
        #factor[factor<=-0.5] = np.nan
        factor.columns = [self.__class__.__name__]
        return factor