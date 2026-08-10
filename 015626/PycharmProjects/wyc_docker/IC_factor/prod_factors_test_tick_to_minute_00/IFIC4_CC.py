# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 13:17:31 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


class IFIC4_CC(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot_if']
        super(IFIC4_CC, self).__init__(required_columns=required_columns)
        
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
        temp = data['close_spot_if'].rolling(60, min_periods = 15).mean() - data['close_spot_if'].shift(20).rolling(40, min_periods = 7).mean()
        factor = temp.to_frame()
        factor.index = data.index
        factor = np.abs(factor)
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        #factor = self.ts_rank(factor)
        #factor[factor<-0.5] = np.nan
        factor.columns = [self.__class__.__name__]
        return factor