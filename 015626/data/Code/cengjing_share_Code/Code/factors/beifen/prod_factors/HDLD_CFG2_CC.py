# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 10:56:58 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class HDLD_CFG2_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['high_zz500', 'low_zz500','close_zz500', 'open_zz500', 'close_spot', 'weight_boolean_zz500']

        super(HDLD_CFG2_CC, self).__init__(required_columns=required_columns
                                  )
    

    

    
    def on_bar(self, data):
        
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        bool_df = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        temp = np.abs(data['close_zz500']-data['open_zz500'])
        temp[temp==0] = 0.01
        temp.index = data['high_zz500'].index
        temp0 = (data['high_zz500'] - data['low_zz500'])
        temp1 = temp0/temp
        a = (data['close_zz500']/data['close_zz500'].shift(1)-1).rolling(30, min_periods = 15).sum()
        vwtc_r = (temp1*(a))#.rolling(20, min_periods = 2).mean()
        factor = (vwtc_r[bool_df]).mean(axis = 1)
        factor.index = data['close_zz500'].index
        factor = factor.to_frame()
        factor = factor.rolling(10, min_periods = 5).mean()
        #print(b.iloc[:, 0].corr(b1.iloc[:, 0]))
        factor2 = ts_rank(factor, 242*3)
        factor2 = factor2.rolling(3, min_periods = 1).mean()
        factor2 = ts_rank(factor2)
        factor2[factor2<=-0.5] = np.nan
        factor2.columns = [self.__class__.__name__]
        return factor2
