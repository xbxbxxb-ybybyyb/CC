# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 18:08:58 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class ZHZH_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot']

        super(ZHZH_ind_CC, self).__init__(
                                  required_columns=required_columns)

    
    def on_bar(self, data):

        temp = (data['high_spot']>=(data['high_spot'].rolling(15, min_periods = 5).max())).astype(int).rolling(60, min_periods = 5).mean()
        factor = ts_rank(temp.to_frame())
        factor.columns = [self.__class__.__name__]
        factor[factor<0] = 0
        return factor