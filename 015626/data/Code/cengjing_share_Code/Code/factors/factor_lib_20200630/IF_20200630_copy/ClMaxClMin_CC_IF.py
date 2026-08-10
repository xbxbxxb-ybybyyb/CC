# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 15:39:28 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class ClMaxClMin_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close', 'recent_month_mask']
 
        super(ClMaxClMin_CC_IF, self).__init__(
                                  required_columns=required_columns)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
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
        m_vwap_ind_r = (data['close']).rolling(40, min_periods = 30).max()/data['close'].rolling(40, min_periods = 30).min()
        factor = m_vwap_ind_r[data['recent_month_mask']].mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor, 242*2)
        factor = factor.rolling(2, min_periods = 1).mean()
        factor = self.ts_rank(factor)
        return factor