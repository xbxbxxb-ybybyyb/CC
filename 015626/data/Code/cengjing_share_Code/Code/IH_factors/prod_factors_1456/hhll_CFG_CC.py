# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 01:04:16 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

# 多头因子
class hhll_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns =['high_zz500', 'low_zz500', 'amount_zz500', 'weight_boolean_zz500']
        
        super(hhll_CFG_CC, self).__init__(
                                  required_columns=required_columns)

    
 
    
    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        d1 = data['high_zz500']>data['high_zz500'].shift(1)
        d2 = data['low_zz500']>data['low_zz500'].shift(1)
        d_f = (d1.astype(int)+d2.astype(int))
        d_f[d_f == 2] = 4

        vwtc_r = d_f.rolling(25, min_periods =15).mean()
        factor = (vwtc_r[stk_amount]).mean(axis = 1)
        #factor.index = data.index
        
        factor = ts_rank(factor.to_frame())
        factor.columns = [self.__class__.__name__]
        return factor