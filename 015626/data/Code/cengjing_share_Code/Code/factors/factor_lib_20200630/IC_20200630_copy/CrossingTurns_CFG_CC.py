# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 09:05:01 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class CrossingTurns_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['high_zz500', 'close_zz500', 'low_zz500', 'open_zz500', 'close_spot', 'weight_boolean_zz500', 'amount_zz500']

        super(CrossingTurns_CFG_CC, self).__init__(required_columns=required_columns
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
        stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        bool_df = stk_index_corr*stk_amount
        temp = np.abs(data['close_zz500']-data['open_zz500'])
        temp[temp==0] = 0.01
        #temp.index = hclose.index
        temp0 = (data['high_zz500'] - data['low_zz500'])
        temp1 = temp0/temp
        a = (data['close_zz500']/data['close_zz500'].shift(1)-1).rolling(30, min_periods = 15).sum()
        vwtc_r = (temp1*(a)).rolling(15, min_periods = 2).mean()
        factor = (vwtc_r[bool_df]).mean(axis = 1)
        factor.index = data['close_zz500'].index
        factor = self.ts_rank(factor.to_frame())
        factor[factor<=-0.5] = np.nan
        #factor = (factor - 0.25)*4/3
        factor.columns = [self.__class__.__name__]
        return factor
