# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 14:40:40 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class SYXWR_nr_wt_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_hs300', 'weight_boolean_hs300', 'weight_hs300', 'low_hs300', 'high_hs300', 'turnover_hs300','open_hs300', 'close_hs300']
        super(SYXWR_nr_wt_CFG_CC_IF, self).__init__(required_columns=required_columns
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
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        stk_weight = (data['weight_hs300'])[data['weight_boolean_hs300']]        
        mask = stk_weight*temp4
        temp1 = pd.DataFrame(np.where(data['open_hs300']>data['close_hs300'], data['open_hs300'], data['close_hs300']))
        temp2 = pd.DataFrame(np.where(data['open_hs300']>data['close_hs300'], data['close_hs300'], data['open_hs300']))
        temp1.index = data['open_hs300'].index
        temp2.index = data['open_hs300'].index
        temp1.columns = data['open_hs300'].columns
        temp2.columns = data['open_hs300'].columns
        b = (data['high_hs300'] - temp1).rolling(30, min_periods = 15).mean()
        b[abs(b)<1e-8] = np.nan
        t_pcor = (data['high_hs300']-temp1)/b
        a = (data['high_hs300'].rolling(30, min_periods = 15).max()-data['low_hs300'].rolling(30, min_periods = 15).min())
        a[abs(a) < 1e-8] = np.nan
        t_pcor2 = (data['close_hs300']-data['low_hs300'].rolling(30, min_periods = 15).min())/a
        t_pcorr = (t_pcor2 - t_pcor)
        tempdf = (t_pcorr*mask).sum(axis = 1).to_frame()
        
        factor = self.normalization(tempdf, 242*5)
        factor[abs(factor)>1] = np.nan
        
        factor = tempdf.rolling(45, min_periods = 10).mean()
        factor = self.ts_rank(factor) 
        factor.columns = [self.__class__.__name__]
        return factor