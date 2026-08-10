# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 14:03:04 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class LminC_ind_CC_vr_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'weight_boolean_zz500', 'low_zz500', 'close_spot']
        super(LminC_ind_CC_vr_CFG_CC, self).__init__(required_columns=required_columns)
    
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
    def ts_std(self, df1, d):
        # moving time-series rank for the past d periods
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                               index=df1.index, name=df1.name)
        return output
    
    def on_bar(self, data):
        '''volatility_sum'''
        stk_close = data['close_zz500']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = self.ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[data['weight_boolean_zz500']]

        '''volatility_rank'''
        mask = 2 * stk_volatility.rank(axis=1, pct=True) - 1
        lltc_ind_r = -data['low_zz500'].rolling(180, min_periods = 90).min()/(data['close_zz500'])
        factor = (lltc_ind_r*mask).sum(axis = 1).to_frame()
        factor = factor.rolling(5, min_periods = 2).mean()
        factor = self.ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor