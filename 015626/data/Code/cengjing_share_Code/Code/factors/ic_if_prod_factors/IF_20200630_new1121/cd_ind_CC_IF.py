# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 16:07:46 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


import numpy as np
from factor_generator import FactorGenerator

# 多头因子
class cd_ind_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns =['close_spot_if']
        
        super(cd_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)
        
    def on_bar(self, data):

        temp = data['close_spot_if'].rolling(60, min_periods = 2).mean().diff()
        factor = temp.to_frame()
        factor.columns =  [self.__class__.__name__]
        factor = rolling_norm(factor, 4800)
        factor[factor<0] = 0
        factor[factor>1] = 0
        return factor
