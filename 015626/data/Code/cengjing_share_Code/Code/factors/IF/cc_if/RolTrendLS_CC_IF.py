# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 15:24:58 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator import FactorGenerator

class RolTrendLS_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_if', 'low_if', 'high_if', 'recent_month_mask']

        super(RolTrendLS_CC_IF, self).__init__(
                                  required_columns=required_columns)
        


    def on_bar(self, data):

        ll = (data['close_if'] - data['low_if'].rolling(120, min_periods = 15).min())-(data['high_if'].rolling(120, min_periods = 15).max() - data['low_if'].rolling(60, min_periods = 15).min())
        a2 = ll.rolling(10, min_periods = 5).mean()
        a3 = a2.rolling(10, min_periods = 5).mean()
        vwtc_r = 3*a3-2*a2
        factor = vwtc_r[data['recent_month_mask']].mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor

