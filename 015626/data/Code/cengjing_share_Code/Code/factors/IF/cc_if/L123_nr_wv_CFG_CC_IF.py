# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 13:08:25 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class L123_nr_wv_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_hs300','weight_boolean_hs300', 'low_hs300', 'turnover_hs300', 'weight_hs300']

        super(L123_nr_wv_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        stk_close = df['close_hs300']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[df['weight_boolean_hs300']]
        stk_weight = (df['weight_hs300'])[df['weight_boolean_hs300']]
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)        
        mask = stk_weight*temp3
        
        hlow = df['low_hs300']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12)
        i2 = rolling_norm(i2)
        tempdf = (i2*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(60, min_periods = 30).mean()
        factor = ts_rank(factor, 2400)
        factor.columns = [self.__class__.__name__]
        return factor