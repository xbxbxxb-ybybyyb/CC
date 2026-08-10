# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 12:49:27 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class LminLmean_nr_corrturn_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_hs300', 'weight_boolean_hs300', 'low_hs300','stk_index_corr_hs300']

        super(LminLmean_nr_corrturn_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        
        turnover = (df['turnover_hs300'].rolling(60, min_periods = 15).mean())[df['weight_boolean_hs300']]   
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        temp2 = df['stk_index_corr_hs300'].gt(pd.Series(df['stk_index_corr_hs300'].quantile(0.80, axis = 1)), axis=0)
        mask = temp4*temp2
        
        ctl_r = -df['low_hs300'].rolling(60, min_periods =15).min()/df['low_hs300'].rolling(30, min_periods =10).mean()
        lltc_ind_r = rolling_norm(ctl_r)
        tempdf = (lltc_ind_r*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(10, min_periods = 5).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor