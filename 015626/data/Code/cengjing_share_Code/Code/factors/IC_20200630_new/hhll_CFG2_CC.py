# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 01:16:25 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

# 多头因子
class hhll_CFG2_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns =['high_zz500', 'low_zz500', 'close_zz500','close_spot', 'weight_boolean_zz500']
        
        super(hhll_CFG2_CC, self).__init__(
                                  required_columns=required_columns)

    
 

    def on_bar(self, data):
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        bool_df = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        d1 = data['high_zz500']>data['high_zz500'].shift(1)
        d2 = data['low_zz500']>data['low_zz500'].shift(1)
        d_f = (d1.astype(int)+d2.astype(int))
        d_f[d_f == 2] = 4

        vwtc_r = d_f.rolling(40, min_periods =15).mean()
        factor = (vwtc_r[bool_df]).mean(axis = 1)
        #factor.index = data.index
        
        factor = ts_rank(factor.to_frame())
        factor.columns = [self.__class__.__name__]
        return factor