# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 09:33:08 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class VLSM_CC(FactorGenerator):
    def __init__(self):
        required_columns=['volume']
        super(VLSM_CC, self).__init__(
                                  required_columns=required_columns,
                                  )
    
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
        vwap_t_r = data['volume'].rolling(60, min_periods = 25).mean()/data['volume'].rolling(90, min_periods = 45).mean()
        factor = vwap_t_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factors = self.normalization(factor)
        return factors

