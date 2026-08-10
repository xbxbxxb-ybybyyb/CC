# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 11:05:26 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator

def normalization(signal, holding_window = 1200): 
    max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
    min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
    a = (signal - min_s)/(max_s-min_s)
    a = 2*a-1
    aa = pd.DataFrame(a)
    aa.index = signal.index
    aa.columns = signal.columns
    return aa

class VwLs_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['vwap_if', 'recent_month_mask']

        super(VwLs_CC_IF, self).__init__(
                                  required_columns=required_columns
                                  )

    def on_bar(self, data):

        price_diff_1 = data['vwap_if']/data['vwap_if'].shift(1)-1
        price_diff_30 = data['vwap_if']/data['vwap_if'].shift(60)-1
        copcor1_r = -(price_diff_1-price_diff_30).rolling(15, min_periods = 5).mean()       
        factor = copcor1_r[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = normalization(factor, 2420)
        # factor[factor>1] = 0
        # factor[factor<=-0.5] = 0
        return factor

