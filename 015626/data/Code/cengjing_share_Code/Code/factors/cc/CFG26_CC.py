# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 17:01:00 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *


class CFG26_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'close_zz500', 'close_spot', 'weight_boolean_zz500']

        super(CFG26_CC, self).__init__(required_columns=required_columns
                                  )
    

            
    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        #stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        bool_df = stk_index_corr[stk_amount]
        hmhm_r = data['close_zz500'].rolling(60, min_periods = 15).mean() - data['close_zz500'].shift(20).rolling(40, min_periods = 7).mean()
        factor = (hmhm_r*bool_df).mean(axis = 1).to_frame()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]
        #factor = factor.rolling(3, min_periods =2).mean()
        factor = rolling_norm(factor, 242*3)
        factor[factor<-0.5]=0
        return factor