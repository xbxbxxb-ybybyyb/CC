# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 13:08:25 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class L123_nr_wv_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_hs300','weight_boolean_hs300', 'low_hs300', 'turnover_hs300', 'weight_hs300']

        super(L123_nr_wv_CFG_CC_IF, self).__init__(required_columns=required_columns
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
    
    def ts_std(self, df1, d):
        # moving time-series rank for the past d periods
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                               index=df1.index, name=df1.name)
        return output
    
    def on_bar(self, df):
        stk_close = df['close_hs300']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = self.ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[df['weight_boolean_hs300']]
        stk_weight = (df['weight_hs300'])[df['weight_boolean_hs300']]
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)        
        mask = stk_weight*temp3
        
        hlow = df['low_hs300']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12)
        i2 = self.normalization(i2)
        tempdf = (i2*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(60, min_periods = 30).mean()
        factor = self.ts_rank(factor, 2400)
        factor.columns = [self.__class__.__name__]
        return factor