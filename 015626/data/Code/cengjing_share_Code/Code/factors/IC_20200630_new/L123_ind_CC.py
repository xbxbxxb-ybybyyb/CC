# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 18:29:27 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class L123_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns=['low_spot']

        super(L123_ind_CC, self).__init__(required_columns=required_columns)

        
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low_spot']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12).rolling(25, min_periods = 2).mean()
        i2 = ts_rank(i2.to_frame())

        i2.columns = [columnname]    
        return i2