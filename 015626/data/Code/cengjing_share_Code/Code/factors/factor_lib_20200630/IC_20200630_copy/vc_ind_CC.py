# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 16:53:24 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator

# 多头因子
class vc_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns =['volume_spot', 'close_spot']

        super(vc_ind_CC, self).__init__(
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
        t_prcd0 = data['volume_spot'].diff().rolling(15, min_periods=7).mean()*(data['close_spot']-data['close_spot'].shift(15))
        factor = t_prcd0.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = -self.normalization(factor)
        factor[factor>1] = 0
        factor[factor<-1] = 0
        return factor