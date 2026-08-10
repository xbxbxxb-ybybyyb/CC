# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 16:06:54 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

# 多头因子
class lma_CC(FactorGenerator):
    def __init__(self):
        required_columns =['low', 'close']
        
        super(lma_CC, self).__init__(
                                  required_columns=required_columns)

    
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
        vwtc_r = (data['low']-data['close'].rolling(120, min_periods = 30).mean())
        factor = vwtc_r.to_frame()
        factor.index = data.index

        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor, 2420)
        factor[factor<-0.5] = np.nan
        factor[factor>1] = np.nan
        return factor

