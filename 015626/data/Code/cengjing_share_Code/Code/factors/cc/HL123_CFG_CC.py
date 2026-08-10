# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 13:30:33 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class HL123_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'high_zz500', 'weight_boolean_zz500']

        super(HL123_CFG_CC, self).__init__(required_columns=required_columns)
    

    
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low_zz500']
        hhigh = df['high_zz500']
        i11 = hhigh.rolling(10, min_periods = 5).max()-hlow.rolling(60, min_periods = 10).min()
        i12 = (hhigh.shift(30)).rolling(10, min_periods = 5).max()-(hlow.shift(30)).rolling(60, min_periods = 10).min()
        i2 = (i11-i12).rolling(5, min_periods = 2).mean()
        i2 = ts_rank(i2[df['weight_boolean_zz500']].mean(axis = 1).to_frame())
        #i2 = rolling_norm(i2)
        #i2[i2>1] = np.nan
        i2[i2<=-0.5] = np.nan
        i2.columns = [columnname]    
        return i2
