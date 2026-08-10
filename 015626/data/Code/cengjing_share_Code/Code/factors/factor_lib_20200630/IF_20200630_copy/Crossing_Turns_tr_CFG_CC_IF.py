# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 10:13:09 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class Crossing_Turns_tr_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['open_hs300','high_hs300','low_hs300', 'amount_hs300','volume_hs300', 'turnover_hs300', 'weight_boolean_hs300', 'close_hs300']

        super(Crossing_Turns_tr_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
        
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, data):
        turnover = (data['turnover_hs300'].rolling(60, min_periods = 15).mean())[data['weight_boolean_hs300']]
        turnover_rank = 2 * turnover.rank(axis=1, pct=True) - 1

        temp = np.abs(pd.DataFrame(np.where(data['open_hs300']-data['close_hs300'] == 0, 0.1, data['open_hs300']-data['close_hs300'])))
        
        temp.index = data['open_hs300'].index
        temp.columns = data['open_hs300'].columns
        temp0 = (data['high_hs300'] - data['low_hs300'])
        temp1 = temp0/temp
        vwap = data['amount_hs300']/data['volume_hs300']
        a = (vwap/vwap.shift(1)-1).rolling(30, min_periods = 15).sum()
        vwtc_r = (temp1*(a)).rolling(25, min_periods = 5).mean()
        
        tempdf = (vwtc_r*turnover_rank).sum(axis = 1).to_frame()
        #factor = self.normalization(tempdf, 242*5)
        #factor[abs(factor)>1] = np.nan
        factor = tempdf.rolling(5, min_periods = 3).mean()
        factor = self.ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor