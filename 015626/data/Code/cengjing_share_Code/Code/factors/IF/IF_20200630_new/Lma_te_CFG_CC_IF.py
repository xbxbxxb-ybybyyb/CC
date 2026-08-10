# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:55:30 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class Lma_te_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_hs300',  'low_hs300', 'turnover_hs300', 'close_hs300', 'weight_boolean_hs300']

        super(Lma_te_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

   
    def on_bar(self, df):
        turnover = (df['turnover_hs300'].rolling(60, min_periods = 15).mean())[df['weight_boolean_hs300']]
        ret_30 = (df['turnover_hs300']/df['turnover_hs300'].shift(30)-1)[df['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0)     
        mask = temp4*temp5
        
        vwtc_r = (df['low_hs300']-df['close_hs300'].rolling(120, min_periods = 30).mean())
        tempdf = (vwtc_r*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(8, min_periods = 2).mean()
        factor = ts_rank(factor)
        factor = factor.rolling(3, min_periods = 1).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
