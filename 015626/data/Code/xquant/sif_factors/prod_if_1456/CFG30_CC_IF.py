# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 14:38:31 2021

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class CFG30_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_hs300', 'weight_boolean_hs300', 'close_hs300']

        super(CFG30_CC_IF, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, data):
        df_s = data['amount_hs300'].rolling(60, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_hs300']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)

        upclose = (data['close_hs300'][bool_df]>data['close_hs300'][bool_df].shift(1)).sum(axis = 1)
        downclose = (data['close_hs300'][bool_df]<data['close_hs300'][bool_df].shift(1)).sum(axis = 1)
        t_prcd2 = (((upclose-downclose)/ (upclose+downclose)).rolling(45, min_periods = 15).mean())
        
        t_prcd2 = t_prcd2.replace([-np.inf,np.inf], np.nan)

        factor = t_prcd2.to_frame()
        factor.columns = [self.__class__.__name__]
        #factor = factor.between_time('13:00', '14:49').groupby(pd.TimeGrouper('D')).mean().dropna(how = 'all')
        factor = ts_rank(factor)
        # factor[factor<0] = 0
        return factor