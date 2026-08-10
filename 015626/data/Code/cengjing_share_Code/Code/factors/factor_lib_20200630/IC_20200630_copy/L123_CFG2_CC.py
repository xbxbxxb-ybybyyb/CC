# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 20:47:18 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class L123_CFG2_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'amount_zz500', 'close_spot', 'weight_boolean_zz500']

        super(L123_CFG2_CC, self).__init__(required_columns=required_columns
                                  )
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
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
        bool_df = stk_index_corr[stk_amount]
        columnname = self.__class__.__name__
        hlow = data['low_zz500']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12).rolling(25, min_periods = 2).mean()
        i2 = (i2*bool_df).mean(axis = 1)
        i2 = self.ts_rank(i2.to_frame())
        #i2 = self.normalization(i2)
        #i2[i2>1] = np.nan
        #i2[i2<=-0.5] = np.nan
        i2.columns = [columnname]    
        return i2