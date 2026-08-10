# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 14:23:45 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class VwLs_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'volume_zz500', 'weight_boolean_zz500']
        
        super(VwLs_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    

    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        #bool_df = 2 * stk_weight.rank(axis=1, pct=True) - 1
        vwap = data['amount_zz500']/data['volume_zz500']
        price_diff_1 = vwap/vwap.shift(1)-1
        price_diff_30 = vwap/vwap.shift(90)-1
        copcor1_r = -(price_diff_1-price_diff_30).rolling(5, min_periods = 1).mean()       
        factor = (bool_df*copcor1_r).mean(axis = 1).to_frame()
        #factor = factor.rolling(10, min_periods = 1).mean()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]

        #factor[factor<=-0.5] = 0
        factor = ts_rank(factor)
        #factor = factor.rolling(3, min_periods = 2).mean()
        factor[factor<=-0.5]=0
        return factor


