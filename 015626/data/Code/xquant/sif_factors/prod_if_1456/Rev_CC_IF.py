# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 15:13:20 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator

class Rev_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_if', 'recent_month_mask']

        super(Rev_CC_IF, self).__init__(
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

        vwtc_r = data['close_if']/data['close_if'].shift(120)-1
        factor = vwtc_r.rolling(3, min_periods = 2).mean()[data['recent_month_mask']].mean(axis = 1).to_frame()
  
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor, 242*8)
        # factor[factor<-1] = 0
        # factor[factor>1] = 0
        return factor

