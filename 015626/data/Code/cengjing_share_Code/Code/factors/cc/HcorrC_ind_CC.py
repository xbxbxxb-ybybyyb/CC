# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 14:46:50 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HcorrC_ind_CC(FactorGenerator):
    def __init__(self):
        
        required_columns =['close_spot', 'high_spot']
        
        super(HcorrC_ind_CC, self).__init__(
                                  required_columns=required_columns)


    
    def on_bar(self, data):


        high = data['high_spot']
        close = data['close_spot']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_pcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)

        t_pcor2[abs(t_pcor2) > 1e8] = 0
        factor = t_pcor2.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 2420)
        return factor
