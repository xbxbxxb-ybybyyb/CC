# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 11:00:43 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *


class CloseVoltoMean_cr_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'weight_boolean_zz500', 'close_spot']
        super(CloseVoltoMean_cr_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    
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
        factor = rolling_norm(factor, 720, method = 'ts_rank')
        factor.columns = [self.__class__.__name__]
        return factor