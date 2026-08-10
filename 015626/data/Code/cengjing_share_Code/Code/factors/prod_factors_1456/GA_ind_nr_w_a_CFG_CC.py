# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 13:23:21 2021

@author: appadmin
"""
#GA_ind_CC_nr_w_a

import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class GA_ind_nr_w_a_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_zz500','amount_zz500', 'close_zz500', 'open_zz500', 'weight_zz500', 'low_zz500', 'high_zz500']

        super(GA_ind_nr_w_a_CFG_CC, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, data):
        df_s = (data['amount_zz500'].rolling(120, min_periods = 15).sum())[data['weight_boolean_zz500']]
        stk_weight = data['weight_zz500']

        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)


        bool_df = stk_weight*temp1

        a = data['high_zz500'].rolling(120, min_periods = 60).max()-data['open_zz500'].shift(120)
        b = data['close_zz500'] - data['low_zz500'].rolling(120, min_periods = 60).min()
        c = (data['high_zz500'].rolling(120, min_periods = 60).max()-data['low_zz500'].rolling(120, min_periods = 60).min())*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = (a+b)/c
        vwtc_r = rolling_norm(vwtc_r, 242)
        factor = (vwtc_r*bool_df).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, 242)
        return factor