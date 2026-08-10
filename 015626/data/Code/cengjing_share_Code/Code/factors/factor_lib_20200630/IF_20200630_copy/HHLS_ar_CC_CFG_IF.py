# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 13:07:56 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class HHLS_ar_CC_CFG_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300',  'high_hs300', 'amount_hs300']

        super(HHLS_ar_CC_CFG_IF, self).__init__(required_columns=required_columns
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

        stk_amount = (data['amount_hs300'])[data['weight_boolean_hs300']]
        
        stk_amount_rank = 2 * stk_amount.rank(axis=1, pct=True) - 1
        mask = stk_amount_rank
        temp = data['high_hs300'].rolling(50, min_periods = 15).max() - data['high_hs300'].shift(50).rolling(50, min_periods = 7).max()
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(5, min_periods = 3).mean()
        factor = self.ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor