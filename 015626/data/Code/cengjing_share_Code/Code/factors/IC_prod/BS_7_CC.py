# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 18:01:27 2021

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class BS_7_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['buy_superorder_money_500', 'buy_bigorder_money_500', 'weight_500', 'amount_500']
        super(BS_7_CC, self).__init__(required_columns=required_columns)
        
    def on_bar(self, data):
        factor = (data['buy_superorder_money_500']+data['buy_bigorder_money_500'])/data['amount_500']
        factor = factor.replace([np.inf, -np.inf], np.nan)
        factor = factor.rolling(15, min_periods = 2).mean()
        df_s = data['amount_500'].rolling(60, min_periods = 5).sum()
        df_s = df_s[data['weight_500']>0]                                                                         
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.9, axis = 1)), axis=0)
        factor = (factor[bool_df]).mean(axis = 1)
        factor = ts_rank(factor.to_frame())
        factor.columns = [self.__class__.__name__]

        return factor