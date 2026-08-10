# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 14:27:25 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class LminLmean_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns =['low_if', 'recent_month_mask']
        super(LminLmean_CC_IF, self).__init__(
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

        ctl_r = -data['low_if'].rolling(90, min_periods =15).min()/data['low_if'].rolling(15, min_periods =5).mean()
        factor = ctl_r[data['recent_month_mask']].mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor, 242*2)
        # factor[factor<-1] =0
        # factor[factor>1] = 0
        return factor