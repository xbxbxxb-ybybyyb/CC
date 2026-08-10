# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 13:18:16 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class cd_ind_nr_at_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_hs300','weight_boolean_hs300', 'close_hs300', 'turnover_hs300']

        super(cd_ind_nr_at_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):

        turnover = (data['turnover_hs300'].rolling(60, min_periods = 15).mean())[data['weight_boolean_hs300']]
        df_s = (data['amount_hs300'].rolling(120, min_periods = 15).sum())[data['weight_boolean_hs300']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        #temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        mask = temp1*temp4
        
        temp = data['close_hs300'].rolling(60, min_periods = 2).mean().diff()
        temp = rolling_norm(temp, 242*5)
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(10, min_periods = 5).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor