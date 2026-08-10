# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:39:52 2020

@author: appadmin
"""

import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class L123_at_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300',  'low_hs300', 'turnover_hs300', 'amount_hs300']

        super(L123_at_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        
        df_s = (df['amount_hs300'].rolling(120, min_periods = 15).sum())[df['weight_boolean_hs300']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        turnover = (df['turnover_hs300'].rolling(60, min_periods = 15).mean())[df['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)        
        mask = temp1*temp4
        
        hlow = df['low_hs300']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12)
        tempdf = (i2*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(30, min_periods = 15).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor