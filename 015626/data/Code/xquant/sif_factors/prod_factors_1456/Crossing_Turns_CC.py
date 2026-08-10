# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 14:58:22 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class Crossing_Turns_CC(FactorGenerator):
    def __init__(self):

        required_columns =['open', 'low', 'close', 'high', 'vwap', 'recent_month_mask']

        super(Crossing_Turns_CC, self).__init__(
                                  required_columns=required_columns)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, data):

        temp = np.abs(pd.DataFrame(np.where(data['open']-data['close'] == 0, 0.1, data['open']-data['close'])))
        temp.index = data['open'].index
        temp.columns = data['open'].columns
        temp = (temp[data['recent_month_mask']]).mean(axis = 1)
        temp0 = ((data['high'] - data['low'])[data['recent_month_mask']]).mean(axis = 1)
        temp1 = temp0/temp
        a = (data['vwap']/data['vwap'].shift(1)-1).rolling(30, min_periods = 15).sum()
        a = (a[data['recent_month_mask']]).mean(axis = 1)
        vwtc_r = (temp1*(a)).rolling(25, min_periods = 5).mean()
        factor = vwtc_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        # factor[factor<=-0.5]=0
        return factor