# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 13:50:53 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


class HHLS_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot']

        super(HHLS_ind_CC, self).__init__(required_columns=required_columns)
    
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
    
    def on_bar(self, data):
        idx = data.index
        data = data.loc[~(((idx.hour==9) & (idx.minute < 30)) | ((idx.hour==11) & (idx.minute == 30)))]
        data = data.sort_index()
        temp = data['high_spot'].rolling(50, min_periods = 15).max() - data['high_spot'].shift(50).rolling(50, min_periods = 7).max()
        factor = temp.to_frame()
        factor.index = data.index
        #factor = np.abs(factor)
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor)
        #factor = self.ts_rank(factor)
        #factor[factor<-0.5] = np.nan
        factor.columns = [self.__class__.__name__]
        return factor
