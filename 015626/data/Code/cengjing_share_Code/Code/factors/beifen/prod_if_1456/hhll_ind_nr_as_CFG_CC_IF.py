# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 10:07:50 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class hhll_ind_nr_as_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_hs300', 'weight_boolean_hs300', 'high_hs300', 'low_hs300']

        super(hhll_ind_nr_as_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        df_s = (data['amount_hs300'].rolling(120, min_periods = 15).sum())[data['weight_boolean_hs300']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        mask = stk_amount
        temp1 = (data['high_hs300']>data['high_hs300'].shift(1)).astype(int)
        temp2 = (data['low_hs300']>data['low_hs300'].shift(1)).astype(int)
        
        temp =  temp1+temp2
        temp[temp==2] = 4
        temp = rolling_norm(temp, 242*5)
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(60, min_periods = 30).mean()
        factor = ts_rank(factor, 2400)
        factor.columns = [self.__class__.__name__]
        return factor