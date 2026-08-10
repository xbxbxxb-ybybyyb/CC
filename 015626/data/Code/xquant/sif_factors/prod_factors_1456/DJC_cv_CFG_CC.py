# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 13:29:44 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class DJC_cv_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'weight_boolean_zz500', 'close_spot']
        super(DJC_cv_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    

    
    def on_bar(self, data):
        stk_close = data['close_zz500']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[data['weight_boolean_zz500']]
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        
        tempp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0)
        tempp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        temp5 = data['close_zz500'].rolling(5, min_periods = 2).mean()
        temp10 = data['close_zz500'].rolling(10, min_periods = 5).mean()
        temp20 = data['close_zz500'].rolling(20, min_periods = 10).mean()
        temp60 = data['close_zz500'].rolling(60, min_periods = 30).mean()
        temp120 = data['close_zz500'].rolling(120, min_periods = 60).mean()
        temp5_diff = (temp5.diff()>0).astype(int)
        temp10_diff = (temp10.diff()>0).astype(int)
        temp20_diff = (temp20.diff()>0).astype(int)
        temp60_diff = (temp60.diff()>0).astype(int)
        temp120_diff = (temp120.diff()>0).astype(int)
        temp = (temp5_diff+temp10_diff+temp20_diff+temp60_diff+temp120_diff).rolling(20, min_periods = 15).mean()
        mask = tempp2 * tempp3
        factor = (temp*mask).sum(axis = 1).to_frame()
        factor = factor.rolling(5, min_periods = 2).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor