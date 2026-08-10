# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 15:25:37 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class RolTrendLS_ind_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'low_spot', 'high_spot']

        super(RolTrendLS_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)
        


    def on_bar(self, data):

        ll = (data['close_spot'] - data['low_spot'].rolling(60, min_periods = 15).min())/(data['high_spot'].rolling(60, min_periods = 15).max() - data['low_spot'].rolling(60, min_periods = 15).min())
        a2 = ll.rolling(10, min_periods = 5).mean()
        a3 = a2.rolling(10, min_periods = 5).mean()
        vwtc_r = 3*a3-2*a2
        factor = vwtc_r.rolling(5, min_periods = 2).mean().to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor
    