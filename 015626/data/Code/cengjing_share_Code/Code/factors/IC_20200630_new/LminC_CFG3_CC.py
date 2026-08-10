# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 16:41:39 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class LminC_CFG3_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'close_spot', 'weight_boolean_zz500']

        super(LminC_CFG3_CC, self).__init__(required_columns=required_columns
                                  )

    
    def on_bar(self, data):
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        cs2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        lltc_ind_r = -data['low_zz500'].rolling(180, min_periods = 90).min()/(data['close_zz500'])
        factor = (lltc_ind_r[cs2]).mean(axis = 1).to_frame()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        #factor[factor>1] = np.nan
        #factor[factor<-0.5] = np.nan
        #factor[factor == np.nan] = 0
        return factor