# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 11:00:43 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class CloseVoltoMean_cr_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'weight_boolean_zz500', 'close_spot']
        super(CloseVoltoMean_cr_CFG_CC, self).__init__(required_columns=required_columns
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
    
        '''corr_sum'''
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]

        '''corr_rank'''
        mask = 2 * stk_index_corr.rank(axis=1, pct=True) - 1
        
        prstd3_r = data['close_zz500'].rolling(40, min_periods =5).std()/data['close_zz500'].rolling(40, min_periods =15).mean()
        factor = (prstd3_r*mask).sum(axis = 1).to_frame()
        factor = factor.rolling(20, min_periods = 10).mean()
        factor = self.ts_rank(factor, 720)
        factor.columns = [self.__class__.__name__]
        return factor