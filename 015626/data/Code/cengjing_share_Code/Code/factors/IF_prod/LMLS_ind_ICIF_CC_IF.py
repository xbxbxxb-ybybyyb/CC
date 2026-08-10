# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:16:19 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class LMLS_ind_ICIF_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'recent_month_mask']

        super(LMLS_ind_ICIF_CC_IF, self).__init__(required_columns=required_columns)
    

    

    def on_bar(self, data):

        temp = data['low'].rolling(75, min_periods = 15).mean() - data['low'].shift(30).rolling(45, min_periods = 7).mean()
        factor = temp[data['recent_month_mask']].mean(axis = 1).to_frame()
        factor = ts_rank(factor)
        factor[factor<-0.5] = 0
        factor.columns = [self.__class__.__name__]
        return factor