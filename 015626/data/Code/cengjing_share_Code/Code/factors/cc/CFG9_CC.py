# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 14:04:15 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *



class CFG9_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'weight_boolean_zz500']

        super(CFG9_CC, self).__init__(required_columns=required_columns
                                  )


    
    def on_bar(self, df):
        columnname = self.__class__.__name__

        hclose = df['close_zz500']
        hret = hclose/hclose.shift(1) - 1
        
        e = hclose.rolling(30, min_periods = 20).max()/hclose.rolling(30, min_periods = 20).min()
        e = e[df['weight_boolean_zz500']]
        hret = hret[df['weight_boolean_zz500']]
        e1 = to_ts(e, hret)
        ee1 = e1.rolling(30, min_periods = 15).mean()
        e2 = rolling_norm(ee1.to_frame())
        e2[e2<=0] = 0
        e2[e2>1] = np.nan
        e2.columns = [columnname]
        #e2.iloc[:, 0] = e2.iloc[:, 0].rolling(3, min_periods = 2).mean()
        return e2
