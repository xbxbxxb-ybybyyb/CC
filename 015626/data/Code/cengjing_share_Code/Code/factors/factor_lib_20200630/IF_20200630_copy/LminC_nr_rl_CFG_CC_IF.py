# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 10:36:54 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class LminC_nr_rl_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300', 'low_hs300', 'turnover_hs300', 'close_hs300']

        super(LminC_nr_rl_CFG_CC_IF, self).__init__(required_columns=required_columns
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
        ret_30 = (df['turnover_hs300']/df['turnover_hs300'].shift(30)-1)[df['weight_boolean_hs300']]
        ret_select = ret_30.gt(pd.Series(ret_30.quantile(0.90, axis = 1)), axis=0)   
        mask = ret_select
        
        lltc_ind_r = -df['low_hs300'].rolling(180, min_periods = 90).min()/(df['close_hs300'])
        lltc_ind_r = self.normalization(lltc_ind_r)
        tempdf = (lltc_ind_r*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(15, min_periods = 8).mean()
        factor = self.ts_rank(factor)
        factor[factor<= 0] = 0
        factor.columns = [self.__class__.__name__]
        return factor