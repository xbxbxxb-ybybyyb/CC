# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 09:34:48 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class hhll_ind_CC_nr_ct_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'close_spot', 'weight_boolean_zz500', 'turnover_zz500', 'high_zz500', 'low_zz500']
        super(hhll_ind_CC_nr_ct_CFG_CC, self).__init__(required_columns=required_columns
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
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        turnover = (data['turnover_zz500'].rolling(60, min_periods = 15).mean())[data['weight_boolean_zz500']]
        temp1 = (data['high_zz500']>data['high_zz500'].shift(1)).astype(int)
        temp2 = (data['low_zz500']>data['low_zz500'].shift(1)).astype(int)
        
        temp =  temp1+temp2
        temp[temp==2] = 4
        factor = temp
        factor = self.normalization(factor)
        
        tempp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0)
        tempp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        mask = tempp2 * tempp4
        factor1 = (factor * mask).sum(axis = 1).to_frame()
        factor1 = factor1.rolling(30, min_periods = 15).mean()
        factor1 = self.ts_rank(factor1)
        factor1.columns = [self.__class__.__name__]
        return factor1
