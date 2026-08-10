# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 18:22:57 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
import numpy as np
from factor_generator import FactorGenerator
from operators_cc import *

class ZHZH_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high', 'recent_month_mask']

        super(ZHZH_CC, self).__init__(
                                  required_columns=required_columns)

    
    
    def on_bar(self, data):

        temp = (data['high']>=(data['high'].rolling(10, min_periods = 5).max())).astype(int).rolling(90, min_periods = 5).mean()
        temp = temp[data['recent_month_mask']].mean(axis = 1).to_frame()
        factor = ts_rank(temp)
        factor[factor<=-0.5] = 0
        factor.columns = [self.__class__.__name__]
        return factor