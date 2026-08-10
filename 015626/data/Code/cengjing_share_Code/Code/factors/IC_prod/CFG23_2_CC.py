# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:47:24 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *



class CFG23_2_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'close_zz500', 'weight_boolean_zz500']

        super(CFG23_2_CC, self).__init__(required_columns=required_columns
                                  )    
            
    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        x = np.array(range(len(data['amount_zz500'])))
        holder = {}
        for item in data['close_zz500'].columns:
            close_spot = data['close_zz500'][item].values
            holder[item] = pd.Series(rolling_linear_reg(x, close_spot, 45))
        temp1 = pd.DataFrame(holder)
        temp1.index = data['close_zz500'].index
        temp = (temp1[bool_df]).mean(axis = 1)
        factor = rolling_norm(temp.to_frame())
        factor.columns = [self.__class__.__name__]
        factor[factor<=-0.5] = 0
        factor[factor>1] = np.nan
        return factor