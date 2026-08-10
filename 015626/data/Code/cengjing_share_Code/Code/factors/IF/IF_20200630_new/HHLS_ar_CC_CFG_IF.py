# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 13:07:56 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class HHLS_ar_CC_CFG_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300',  'high_hs300', 'amount_hs300']

        super(HHLS_ar_CC_CFG_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):

        stk_amount = (data['amount_hs300'])[data['weight_boolean_hs300']]
        
        stk_amount_rank = 2 * stk_amount.rank(axis=1, pct=True) - 1
        mask = stk_amount_rank
        temp = data['high_hs300'].rolling(50, min_periods = 15).max() - data['high_hs300'].shift(50).rolling(50, min_periods = 7).max()
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(5, min_periods = 3).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor