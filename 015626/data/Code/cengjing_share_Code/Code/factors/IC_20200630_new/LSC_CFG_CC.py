# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 13:20:46 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class LSC_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'close_spot', 'amount_zz500', 'high_zz500', 'weight_boolean_zz500']

        super(LSC_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    
    def on_bar(self, data):
        df_s = (data['amount_zz500'].rolling(120, min_periods = 15).sum())
        df_s = df_s[data['weight_boolean_zz500']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        #stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        bool_df = stk_index_corr*stk_amount
        hh = (data['high_zz500'].rolling(30, min_periods = 10).max() - data['close_zz500'])/(data['high_zz500'].rolling(30, min_periods = 10).max() - data['low_zz500'].rolling(30, min_periods = 10).min()) 
        ll = (data['close_zz500'] - data['low_zz500'].rolling(30, min_periods = 10).min())/(data['high_zz500'].rolling(30, min_periods = 10).max() - data['low_zz500'].rolling(30, min_periods = 10).min())
        hh[abs(hh)>100000] = np.nan
        ll[abs(ll)>100000] = np.nan
        vwtc_r = ll.rolling(15, min_periods = 5).mean()-hh.rolling(15, min_periods = 5).mean()
        factor = (vwtc_r[data['weight_boolean_zz500']]*bool_df).mean(axis = 1).to_frame()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = factor.rolling(3, min_periods = 1).mean()
        factor = ts_rank(factor)

        #factor[factor<=-0.5] = np.nan
        return factor