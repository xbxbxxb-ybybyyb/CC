# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:51:35 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class ZHZH_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'high_zz500', 'weight_boolean_zz500']
        
        super(ZHZH_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    
    
    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        temp = (data['high_zz500']>=(data['high_zz500'].rolling(30, min_periods = 5).max())).astype(int).rolling(40, min_periods = 5).mean()
        temp = (temp[bool_df]).mean(axis = 1)
        factor = ts_rank(temp.to_frame())
        #factor = ts_rank(factor)
        #factor[factor<=-0.5] = np.nan
        factor.columns = [self.__class__.__name__]
        return factor