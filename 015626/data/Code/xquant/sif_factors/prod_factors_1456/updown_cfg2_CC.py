# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 13:29:53 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

# demo
class updown_cfg2_CC(FactorGeneratorComplex):
    def __init__(self):

        required_columns =['close_zz500', 'amount_zz500', 'weight_boolean_zz500']

        super(updown_cfg2_CC, self).__init__(
                                  required_columns=required_columns)
        
            


    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        hclose = (data['close_zz500']/data['close_zz500'].shift(1)-1)
        #upclose = ((hclose>0) * stk_amount).sum(axis = 1)
        #downclose = ((hclose<0) * stk_amount).sum(axis = 1)

        upclose = stk_amount[hclose>0].sum(axis=1)
        downclose = stk_amount[hclose<0].sum(axis=1)

        vwtc_r = ((upclose-downclose)/ (upclose+downclose)).rolling(90, min_periods = 45).mean()
        vwtc_r[abs(vwtc_r)>10000] = np.nan
        factor = vwtc_r.to_frame()
        
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
