# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 16:06:54 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

# 多头因子
class lma_CC(FactorGenerator):
    def __init__(self):
        required_columns =['low', 'close', 'recent_month_mask']
        
        super(lma_CC, self).__init__(
                                  required_columns=required_columns)


    def on_bar(self, data):

        vwtc_r = (data['low']-data['close'].rolling(120, min_periods = 30).mean())
        factor = (vwtc_r[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        factor[factor<=-0.5] = 0
        factor[factor>1] = 0
        return factor
