# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 10:09:00 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class hhll_nr_we_CC_CFG_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_hs300','turnover_hs300', 'weight_boolean_hs300', 'close_hs300', 'high_hs300', 'low_hs300']

        super(hhll_nr_we_CC_CFG_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        ret_30 = (data['turnover_hs300']/data['turnover_hs300'].shift(30)-1)[data['weight_boolean_hs300']]
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0)
        stk_weight = (data['weight_hs300'])[data['weight_boolean_hs300']]
        mask = temp5*stk_weight
        temp1 = (data['high_hs300']>data['high_hs300'].shift(1)).astype(int)
        temp2 = (data['low_hs300']>data['low_hs300'].shift(1)).astype(int)
        
        temp =  temp1+temp2
        temp[temp==2] = 4
        temp = rolling_norm(temp, 242*5)
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(60, min_periods = 30).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor