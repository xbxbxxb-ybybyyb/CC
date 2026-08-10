# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 16:25:14 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from operators_cc import *

class Rev_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close', 'recent_month_mask']

        super(Rev_CC, self).__init__(
                                  required_columns=required_columns)


    def on_bar(self, data):
        vwtc_r = data['close']/data['close'].shift(180)-1
        vwtc_r = (vwtc_r[data['recent_month_mask']]).mean(axis = 1)
        factor = vwtc_r.rolling(3, min_periods = 2).mean().to_frame()
        factor = rolling_norm(factor, 2420)
        factor[factor<-0.5] = 0
        factor[factor>1] = 0
        factor.columns = [self.__class__.__name__]
        return factor