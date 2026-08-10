# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 10:36:54 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class LminC_nr_rl_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300', 'low_hs300', 'turnover_hs300', 'close_hs300']

        super(LminC_nr_rl_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        ret_30 = (df['turnover_hs300']/df['turnover_hs300'].shift(30)-1)[df['weight_boolean_hs300']]
        ret_select = ret_30.gt(pd.Series(ret_30.quantile(0.90, axis = 1)), axis=0)   
        mask = ret_select
        
        lltc_ind_r = -df['low_hs300'].rolling(180, min_periods = 90).min()/(df['close_hs300'])
        lltc_ind_r = rolling_norm(lltc_ind_r)
        tempdf = (lltc_ind_r*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(15, min_periods = 8).mean()
        factor = ts_rank(factor)
        factor[factor<= 0] = 0
        factor.columns = [self.__class__.__name__]
        return factor