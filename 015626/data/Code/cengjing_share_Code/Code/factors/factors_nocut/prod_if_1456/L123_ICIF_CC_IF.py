# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:33:13 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class L123_ICIF_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'recent_month_mask']

        super(L123_ICIF_CC_IF, self).__init__(required_columns=required_columns)
    

    

    
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12).rolling(30, min_periods = 20).mean()
        i2 = ts_rank(i2[df['recent_month_mask']].mean(axis = 1).to_frame())
        #i2 = rolling_norm(i2)
        # i2[i2>1] = 0
        # i2[i2<=-0.5] = 0
        i2.columns = [columnname]    
        return i2