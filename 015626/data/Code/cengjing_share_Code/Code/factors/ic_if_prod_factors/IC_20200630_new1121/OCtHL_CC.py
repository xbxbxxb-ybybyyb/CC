# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 14:12:29 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class OCtHL_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high', 'low', 'close', 'open', 'recent_month_mask']

        super(OCtHL_CC, self).__init__(
                                  required_columns=required_columns)


    def on_bar(self, data):
        temp1 = data['open'] - data['close']
        temp2 = data['high'] - data['low']
        temp2[abs(temp2)<1e-8] = np.nan
        t_pcor2 = -temp1/temp2
        t_pcor2[abs(t_pcor2) > 1e8] = 0
        t_pcor2 = t_pcor2.rolling(30, min_periods = 15).mean().rolling(5, min_periods = 2).mean()
        
        factor = (t_pcor2[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor