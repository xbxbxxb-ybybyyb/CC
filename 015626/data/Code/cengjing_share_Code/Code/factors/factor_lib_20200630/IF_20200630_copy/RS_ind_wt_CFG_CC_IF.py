# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 09:42:38 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class RS_ind_wt_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_hs300', 'turnover_hs300', 'weight_boolean_hs300', 'close_hs300']

        super(RS_ind_wt_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
        
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, df):
        stk_weight = (df['weight_hs300'])[df['weight_boolean_hs300']]
        turnover = (df['turnover_hs300'].rolling(60, min_periods = 15).mean())[df['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        wt = stk_weight*temp4
        ret = df['close_hs300']/df['close_hs300'].shift(1)-1
        a = ret.rolling(25, min_periods = 15).std()
        a[abs(a)<1e-8] = np.nan
        i1 = (df['close_hs300']/df['close_hs300'].shift(24)-1) / a
        
        tempdf = (i1*wt).sum(axis = 1)
        factor = tempdf.rolling(8, min_periods = 4).mean().to_frame()
        factor = self.ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor