# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 09:59:40 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *


class GA_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['open_zz500', 'close_zz500', 'amount_zz500',  'high_zz500', 'low_zz500', 'weight_boolean_zz500']

        super(GA_CFG_CC, self).__init__(required_columns=required_columns
                                  )
    

    
    def on_bar(self, data):

        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        
        a = data['high_zz500'].rolling(120, min_periods = 60).max()-data['open_zz500'].shift(120)
        b = data['close_zz500'] - data['low_zz500'].rolling(120, min_periods = 60).min()
        c = (data['high_zz500'].rolling(120, min_periods = 60).max()-data['low_zz500'].rolling(120, min_periods = 60).min())*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = (a+b)/c
        factor = (vwtc_r[bool_df]).mean(axis = 1)
        #factor.iloc[:, 0] = factor.iloc[:, 0].rolling(5, min_periods = 2).mean()
        factor = ts_rank(factor.to_frame())
        #factor = ts_rank(factor)
        #factor[factor<-0.5] = np.nan
        factor.columns = [self.__class__.__name__]
        return factor
