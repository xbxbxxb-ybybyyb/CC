# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 17:58:03 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np

# 多头因子
class cmh_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns =['high_zz500', 'close_zz500', 'close_spot', 'weight_boolean_zz500']
        
        super(cmh_CFG_CC, self).__init__(
                                  required_columns=required_columns)

    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa 

    def on_bar(self, data):
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        bool_df = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        vwtc_r = (data['high_zz500']-data['close_zz500'].rolling(60, min_periods = 30).mean())
        factor = (vwtc_r[bool_df]).mean(axis = 1).to_frame()
        #factor.index = data.index

        
        factor = self.ts_rank(factor, 1000)
        factor = factor.rolling(2, min_periods = 1).mean()
        factor = self.ts_rank(factor)

        factor[factor<=-0.5] = 0
        factor.columns = [self.__class__.__name__]
        return factor