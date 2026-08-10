# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:12:50 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class VLSM_CFG2_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'volume_zz500', 'weight_boolean_zz500']
        
        super(VLSM_CFG2_CC, self).__init__(required_columns=required_columns
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
        stk_amount = (data['amount_zz500'])[data['weight_boolean_zz500']]
        bool_df = 2 * stk_amount.rank(axis=1, pct=True) - 1
        
        vwap = data['amount_zz500']/data['volume_zz500']
        price_diff_1 = vwap/vwap.shift(1)-1
        price_diff_30 = vwap/vwap.shift(30)-1
        copcor1_r = -(price_diff_1-price_diff_30)#.rolling(10, min_periods = 1).mean()       
        factor = (bool_df*copcor1_r[data['weight_boolean_zz500']]).mean(axis = 1).to_frame()
        factor = factor.rolling(10, min_periods = 1).mean()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]

        #factor[factor<=-0.5] = 0
        factor = self.ts_rank(factor)
        #factor = factor.rolling(3, min_periods = 2).mean()
        factor = self.ts_rank(factor)
        factor[factor<=-0.5]=0
        return factor
