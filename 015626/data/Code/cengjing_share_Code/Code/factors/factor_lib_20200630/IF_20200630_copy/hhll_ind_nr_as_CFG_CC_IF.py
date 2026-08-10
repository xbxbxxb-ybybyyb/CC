# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 10:07:50 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class hhll_ind_nr_as_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_hs300', 'weight_boolean_hs300', 'high_hs300', 'low_hs300']

        super(hhll_ind_nr_as_CFG_CC_IF, self).__init__(required_columns=required_columns
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
    
    def on_bar(self, data):
        df_s = (data['amount_hs300'].rolling(120, min_periods = 15).sum())[data['weight_boolean_hs300']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        mask = stk_amount
        temp1 = (data['high_hs300']>data['high_hs300'].shift(1)).astype(int)
        temp2 = (data['low_hs300']>data['low_hs300'].shift(1)).astype(int)
        
        temp =  temp1+temp2
        temp[temp==2] = 4
        temp = self.normalization(temp, 242*5)
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(60, min_periods = 30).mean()
        factor = self.ts_rank(factor, 2400)
        factor.columns = [self.__class__.__name__]
        return factor