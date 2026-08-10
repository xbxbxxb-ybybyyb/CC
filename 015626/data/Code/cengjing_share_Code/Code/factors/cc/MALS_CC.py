# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 13:46:14 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class MALS_CC(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'recent_month_mask']

        super(MALS_CC, self).__init__(required_columns=required_columns)

    
    def on_bar(self, data):

        temp = data['close'].rolling(60, min_periods = 15).mean() - data['close'].shift(20).rolling(40, min_periods = 7).mean()
        temp = (temp[data['recent_month_mask']]).mean(axis = 1)
        factor = temp.rolling(3, min_periods = 1).mean().to_frame()
       
        factor = np.abs(factor)
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, 2420)
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor