# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 10:55:03 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class L123_CC_nr_vs_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'weight_boolean_zz500', 'low_zz500']
        super(L123_CC_nr_vs_CFG_CC, self).__init__(required_columns=required_columns
                                  )


    
    def on_bar(self, df):

        hlow = df['low_zz500']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12)
        ii2 = rolling_norm(i2)
        stk_close = df['close_zz500']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        mask = stk_volatility[df['weight_boolean_zz500']]
        factor = (ii2*mask).sum(axis = 1).to_frame()
        factor = factor.rolling(40, min_periods = 20).mean()
        factor = ts_rank(factor, 720)
        factor.columns = [self.__class__.__name__]
        return factor