# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 13:28:00 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HL123_CC(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'recent_month_mask']

        super(HL123_CC, self).__init__(required_columns=required_columns)

    
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low']
        hhigh = df['high']
        i11 = hhigh.rolling(10, min_periods = 5).max()-hlow.rolling(60, min_periods = 10).min()
        i12 = (hhigh.shift(30)).rolling(10, min_periods = 5).max()-(hlow.shift(30)).rolling(60, min_periods = 10).min()
        i2 = ((i11-i12).rolling(20, min_periods = 2).mean())[df['recent_month_mask']]
        i2 = ts_rank(i2.mean(axis = 1).to_frame())
        i2[i2<=0] = 0
        i2.columns = [columnname]    
        return i2