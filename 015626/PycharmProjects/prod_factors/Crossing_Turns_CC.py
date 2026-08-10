# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:52:23 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class Crossing_Turns_CC(FactorGenerator):
    def __init__(self):

        required_columns =['open', 'low', 'close', 'high', 'vwap']

        super(Crossing_Turns_CC, self).__init__(
                                  required_columns=required_columns)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, data):
        idx = data.index
        data = data.loc[~(((idx.hour==9) & (idx.minute < 30)) | ((idx.hour==11) & (idx.minute == 30)))]
        data = data.sort_index()
        temp = np.abs(pd.Series(np.where(data['open']-data['close'] == 0, 0.1, data['open']-data['close'])))
        temp0 = (data['high'] - data['low']).reset_index(drop = True)
        temp1 = temp0/temp
        a = (data['vwap']/data['vwap'].shift(1)-1).rolling(30, min_periods = 15).sum().reset_index(drop = True)
        vwtc_r = (temp1*(a)).rolling(10, min_periods = 5).mean()
        factor = vwtc_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        factor[factor<-0.7]=np.nan
        return factor
