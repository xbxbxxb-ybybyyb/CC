# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 17:44:46 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator

# demo
class HLDL2_ind_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot_if', 'low_spot_if']

        super(HLDL2_ind_CC_IF, self).__init__(
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


        t_pcorr = (data['high_spot_if'].diff()+data['low_spot_if'].diff()).rolling(90, min_periods = 45).mean()
        factor = t_pcorr.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor)
        factor[factor<0] = 0
        return factor
