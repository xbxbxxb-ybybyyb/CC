# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 15:53:04 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator

class CloseVoltoMean_CC_IF_aug(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if']

        super(CloseVoltoMean_CC_IF_aug, self).__init__(
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

        prstd3_r = data['close_spot_if'].rolling(90, min_periods =10).std()/data['close_spot_if'].rolling(90, min_periods =15).mean()
        factor = prstd3_r.to_frame()

        factor.columns =  [self.__class__.__name__]
        factor = self.normalization(factor)
        factor[factor>1] = 0
        factor[factor<=-0.5] = 0
        return factor
    
