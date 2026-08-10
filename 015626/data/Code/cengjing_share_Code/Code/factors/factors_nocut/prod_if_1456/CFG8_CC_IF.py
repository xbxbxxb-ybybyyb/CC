# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 11:09:22 2021

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class CFG8_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300','volume_hs300', 'close_hs300', 'float_shares_hs300']

        super(CFG8_CC_IF, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hvolume = df['volume_hs300']
        hclose = df['close_hs300']
        hfs = df['float_shares_hs300']
        hret = hclose/hclose.shift(1) - 1
        d1 = hvolume/hclose/hfs
        
        hret = hret.replace([-np.inf, np.inf], np.nan)
        d1 = d1.replace([-np.inf, np.inf], np.nan)
        
        d1 = d1[df['weight_boolean_hs300']]
        hret = hret[df['weight_boolean_hs300']]
        d1 = to_ts(d1, hret)
        dd1 = d1.rolling(45, min_periods = 15).mean()
        dd2 = rolling_norm(dd1.to_frame())
        dd2.columns = [columnname]
        # dd2[dd2<=-0.5] = 0
        # dd2[dd2>1] = np.nan
        
        return dd2
