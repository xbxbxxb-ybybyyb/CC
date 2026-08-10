# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 14:22:15 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

 
from factor_generator_complex import FactorGeneratorComplex

class ZHZH_vt_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_hs300', 'close_hs300', 'weight_boolean_hs300', 'high_hs300']
        super(ZHZH_vt_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        
        turnover = (data['turnover_hs300'].rolling(60, min_periods = 15).mean())[data['weight_boolean_hs300']]
        stk_close = data['close_hs300']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[data['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0) 
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        mask = temp3*temp4
        
        temp = (data['high_hs300']>=(data['high_hs300'].rolling(10, min_periods = 5).max())).astype(int).rolling(90, min_periods = 5).mean()
        
        tempdf = (temp*mask)
        tempdf = tempdf.mean(axis = 1).to_frame()
        factor = tempdf.rolling(15, min_periods = 8).mean()
        factor = ts_rank(factor)
        
        factor.columns = [self.__class__.__name__]
        return factor