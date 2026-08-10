# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 08:55:09 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HDL_CC(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'recent_month_mask']
        super(HDL_CC, self).__init__(required_columns=required_columns)
        
    
    def on_bar(self, data):

        hdl_r = (data['high'].rolling(25, min_periods = 10).max())/(data['low'].rolling(25, min_periods = 10).min())
        factor = ((hdl_r.rolling(10, min_periods = 2).mean())[data['recent_month_mask']]).mean(axis =1).to_frame()
        factor.columns = [self.__class__.__name__]
        factors = ts_rank(factor)
        # factors[factors<=-0.5] = 0
        return factors