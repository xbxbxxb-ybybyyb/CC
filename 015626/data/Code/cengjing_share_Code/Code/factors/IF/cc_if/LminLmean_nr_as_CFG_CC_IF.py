# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 11:13:43 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class LminLmean_nr_as_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_hs300', 'weight_boolean_hs300', 'low_hs300']

        super(LminLmean_nr_as_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        df_s = (df['amount_hs300'].rolling(120, min_periods = 15).sum())[df['weight_boolean_hs300']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)   
        mask = stk_amount
        
        ctl_r = -df['low_hs300'].rolling(60, min_periods =15).min()/df['low_hs300'].rolling(30, min_periods =10).mean()
        lltc_ind_r = rolling_norm(ctl_r)
        tempdf = (lltc_ind_r*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(8, min_periods = 4).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor