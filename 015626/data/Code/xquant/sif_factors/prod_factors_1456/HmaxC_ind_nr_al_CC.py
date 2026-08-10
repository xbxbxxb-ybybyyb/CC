# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 10:33:02 2021

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class HmaxC_ind_nr_al_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'weight_boolean_zz500', 'weight_zz500', 'turnover_zz500', 'high_zz500', 'close_zz500']

        super(HmaxC_ind_nr_al_CC, self).__init__(required_columns=required_columns
                                  )
        
        
    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(60, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        turnover = (data['turnover_zz500'].rolling(60, min_periods = 15).mean())[data['weight_boolean_zz500']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        bool_df = temp1&temp4
        
        hmhm_r = -data['high_zz500'].rolling(120, min_periods = 90).max()/data['close_zz500']
        hmhm_r = rolling_norm(hmhm_r, 242)
        factor = hmhm_r[bool_df].mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        #factor = factor.between_time('13:00', '14:49').groupby(pd.TimeGrouper('D')).mean().dropna(how = 'all')
        factor = rolling_norm(factor, 242)
        #factor[factor<0] = 0
        return factor