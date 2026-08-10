# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 14:22:15 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class ZHZH_vt_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_hs300', 'close_hs300', 'weight_boolean_hs300', 'high_hs300']
        super(ZHZH_vt_CFG_CC_IF, self).__init__(required_columns=required_columns
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
        
        turnover = (data['turnover_hs300'].rolling(60, min_periods = 15).mean())[data['weight_boolean_hs300']]
        stk_close = data['close_hs300']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = self.ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[data['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0) 
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        mask = temp3*temp4
        
        temp = (data['high_hs300']>=(data['high_hs300'].rolling(10, min_periods = 5).max())).astype(int).rolling(90, min_periods = 5).mean()
        
        tempdf = (temp*mask)
        tempdf = tempdf.mean(axis = 1).to_frame()
        factor = tempdf.rolling(15, min_periods = 8).mean()
        factor = self.ts_rank(factor)
        
        factor.columns = [self.__class__.__name__]
        return factor