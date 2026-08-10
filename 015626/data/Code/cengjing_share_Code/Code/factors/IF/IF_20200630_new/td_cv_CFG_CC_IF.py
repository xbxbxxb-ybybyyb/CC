# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 13:50:40 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class td_cv_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['stk_index_corr_hs300', 'weight_boolean_hs300', 'close_hs300', 'low_hs300', 'high_hs300']
        super(td_cv_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        stk_close = data['close_hs300']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[data['weight_boolean_hs300']]
        stk_index_corr = data['stk_index_corr_hs300']
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        temp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0) 
        mask = temp2 * temp3
        
        temp = data['low_hs300'].rolling(10, min_periods = 5).min()-data['low_hs300'].rolling(60, min_periods = 5).min()+data['high_hs300'].rolling(10, min_periods = 5).max()-data['high_hs300'].rolling(60, min_periods = 5).max()

        tempdf = (temp*mask)
        tempdf = tempdf.mean(axis = 1).to_frame()
        factor = tempdf.rolling(15, min_periods = 7).mean()
        factor = ts_rank(factor, 720)
        
        factor.columns = [self.__class__.__name__]
        return factor