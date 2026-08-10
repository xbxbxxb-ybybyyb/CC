# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 18:03:23 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class CFG23_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'close_zz500', 'close_spot', 'weight_boolean_zz500']

        super(CFG23_CC, self).__init__(required_columns=required_columns
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
    
    def rolling_linear_reg(self, x, y, window_size):
        x2=np.power(x,2)
        xy=x*y
        window = np.ones(int(window_size))
        a1=np.convolve(xy, window, 'full')*window_size
        a2=np.convolve(x, window, 'full')*np.convolve(y, window, 'full')
        b1=np.convolve(x2, window, 'full')*window_size
        b2=np.power(np.convolve(x, window, 'full'),2)
        alphas=(a1-a2)/(b1-b2)
        betas=(np.convolve(y, window, 'full')-alphas*np.convolve(x, window, 'full'))/float(window_size)
        alphas=alphas[:-1*(window_size-1)] #numpy array of rolled alpha
        betas=betas[:-1*(window_size-1)] 
        alphas[:window_size-1] = np.nan
        return alphas
    
    def on_bar(self, data):
        index_close = data['close_spot']
        stk_close = data['close_zz500']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        bool_df = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        x = np.array(range(len(data['close_zz500'])))
        holder = {}
        for item in data['close_zz500'].columns:
            close_spot = data['close_zz500'][item].values
            holder[item] = pd.Series(self.rolling_linear_reg(x, close_spot, 60))
        temp1 = pd.DataFrame(holder)
        temp1.index = data['close_zz500'].index
        temp1.columns = data['close_zz500'].columns
        temp = (temp1[bool_df]).mean(axis = 1)
        factor = self.normalization(temp.to_frame())
        factor.columns = [self.__class__.__name__]
        factor[factor<=0] = 0
        return factor
    