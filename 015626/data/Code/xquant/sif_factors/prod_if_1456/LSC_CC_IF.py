# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 14:23:00 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class LSC_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['high_if', 'low_if', 'close_if', 'recent_month_mask']

        super(LSC_CC_IF, self).__init__(
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

        a = (data['high_if'].rolling(30, min_periods = 10).max() - data['low_if'].rolling(30, min_periods = 10).min())
        b = (data['high_if'].rolling(30, min_periods = 10).max() - data['low_if'].rolling(30, min_periods = 10).min())
        a[abs(a) < 1e-8] = np.nan
        b[abs(b) < 1e-8] = np.nan
        hh = (data['high_if'].rolling(30, min_periods = 10).max() - data['close_if'])/a
        ll = (data['close_if'] - data['low_if'].rolling(30, min_periods = 10).min())/b
        vwtc_r = ll.rolling(90, min_periods = 15).mean()-hh.rolling(90, min_periods = 15).mean()
        factor = vwtc_r[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor)
        # factor[factor<=-0.5] = 0
        # factor[factor>1] = 0
        return factor
