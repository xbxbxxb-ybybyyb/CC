# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 08:45:14 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class hhll_t3_CC_CFG_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_hs300', 'weight_boolean_hs300', 'close_hs300', 'high_hs300', 'low_hs300']

        super(hhll_t3_CC_CFG_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        turnover = (df['turnover_hs300'].rolling(60, min_periods = 15).mean())[df['weight_boolean_hs300']]
        ret = (df['close_hs300']/df['close_hs300'].shift(30)-1)[df['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        temp6 = ret.gt(pd.Series(ret.quantile(0.80, axis = 1)), axis=0)
        mask = temp4*temp6
        temp1 = (df['high_hs300']>df['high_hs300'].shift(1)).astype(int)
        temp2 = (df['low_hs300']>df['low_hs300'].shift(1)).astype(int)
        
        temp =  temp1+temp2
        temp[temp==2] = 4
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(60, min_periods = 2).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor