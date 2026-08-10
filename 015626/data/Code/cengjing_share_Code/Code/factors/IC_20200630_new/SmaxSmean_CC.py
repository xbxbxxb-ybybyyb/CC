# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:00:17 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class SmaxSmean_CC(FactorGenerator):
    def __init__(self):
        required_columns =['share', 'recent_month_mask']
        super(SmaxSmean_CC, self).__init__(
                                  required_columns=required_columns)
    

    def on_bar(self, data):

        pd1_r = data['share'].rolling(30, min_periods = 5).mean() - data['share'].rolling(120, min_periods = 75).mean()
        factor = (pd1_r[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        factor[factor<=-0.5] = 0
        return factor


