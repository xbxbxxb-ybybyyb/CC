# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 18:26:51 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class L123_CC(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'recent_month_mask']

        super(L123_CC, self).__init__(required_columns=required_columns)

    
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12).rolling(30, min_periods = 2).mean()
        i2 = (i2[df['recent_month_mask']]).mean(axis = 1)
        i2 = ts_rank(i2.to_frame())

        i2[i2<=0] = 0
        i2.columns = [columnname]    
        return i2