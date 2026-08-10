# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 19:50:40 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class L123_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'weight_boolean_zz500']

        super(L123_CFG_CC, self).__init__(required_columns=required_columns
                                  )
 
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low_zz500']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12).rolling(30, min_periods = 2).mean()
        i2 = (i2[df['weight_boolean_zz500']]).mean(axis = 1)
        i2 = ts_rank(i2.to_frame())
        #i2 = rolling_norm(i2)
        # i2[i2>1] = np.nan
        #i2[i2<=-0.5] = np.nan
        i2.columns = [columnname]    
        return i2