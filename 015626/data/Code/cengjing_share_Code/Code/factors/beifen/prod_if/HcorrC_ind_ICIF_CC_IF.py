# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 17:25:40 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class HcorrC_ind_ICIF_CC_IF(FactorGenerator):
    def __init__(self):
        
        required_columns =['close_spot', 'high_spot']
        
        super(HcorrC_ind_ICIF_CC_IF, self).__init__(
                                  required_columns=required_columns)


    
    def on_bar(self, data):
        high = data['high_spot']
        close = data['close_spot']
        s = high.rolling(45, min_periods=30).std()
        f = close.rolling(45, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_pcor2 = high.rolling(45, min_periods=30).cov(close) / (s * f)
        factor = t_pcor2.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = factor.rolling(30, min_periods = 7).mean()
        factor = ts_rank(factor)  
        return factor


