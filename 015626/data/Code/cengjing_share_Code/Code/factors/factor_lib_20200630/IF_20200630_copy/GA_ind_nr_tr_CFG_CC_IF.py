# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 18:19:29 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class GA_ind_nr_tr_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['high_hs300','open_hs300', 'low_hs300', 'weight_boolean_hs300', 'close_hs300', 'turnover_hs300']

        super(GA_ind_nr_tr_CFG_CC_IF, self).__init__(required_columns=required_columns
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
        turnover_rank = 2 * turnover.rank(axis=1, pct=True) - 1
        mask = turnover_rank
        a = data['high_hs300'].rolling(120, min_periods = 60).max()-data['open_hs300'].shift(120)
        b = data['close_hs300'] - data['low_hs300'].rolling(120, min_periods = 60).min()
        c = (data['high_hs300'].rolling(120, min_periods = 60).max()-data['low_hs300'].rolling(120, min_periods = 60).min())*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = (a+b)/c
        vwtc_r = self.normalization(vwtc_r)
        tempdf = (vwtc_r*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(5, min_periods = 2).mean()
        factor = self.ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor