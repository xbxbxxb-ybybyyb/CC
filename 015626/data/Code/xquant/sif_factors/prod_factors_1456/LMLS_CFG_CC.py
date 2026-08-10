# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 00:38:19 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class LMLS_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'close_spot', 'weight_boolean_zz500']

        super(LMLS_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    
    def on_bar(self, data):
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        
        '''corr_rank'''
        stk_index_corr_rank = 2 * stk_index_corr.rank(axis=1, pct=True) - 1
        temp = data['low_zz500'].rolling(50, min_periods = 15).mean() - data['low_zz500'].shift(20).rolling(30, min_periods = 7).mean()
        factor = (temp*stk_index_corr_rank).mean(axis = 1).to_frame()
        factor.index = data['low_zz500'].index
        #factor = np.abs(factor)
        factor.columns = [self.__class__.__name__]
        #factor = rolling_norm(factor)
        factor = factor#.rolling(3, min_periods = 2).mean()
        factor = ts_rank(factor)
        #factor[factor<-0.5] = np.nan
        #factor.columns = [self.__class__.__name__]
        
        return factor