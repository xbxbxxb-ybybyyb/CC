# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 09:45:52 2020

@author: appadmin
"""

import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class CFG21_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'weight_zz500', 'weight_boolean_zz500']

        super(CFG21_CC, self).__init__(required_columns=required_columns
                                  )

            
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low_zz500']
        hweight = df['weight_zz500']
        #weight = df['weight_zz500'].xs('weight_zz500', axis=1, drop_level=True)
        
        a = -hlow.rolling(60, min_periods =15).min()/hlow.rolling(15, min_periods =5).mean()
        htemp = ((a[df['weight_boolean_zz500']])*hweight).mean(axis = 1)

        htemp = rolling_norm(htemp.to_frame())

        htemp.columns = [columnname]

        return htemp
