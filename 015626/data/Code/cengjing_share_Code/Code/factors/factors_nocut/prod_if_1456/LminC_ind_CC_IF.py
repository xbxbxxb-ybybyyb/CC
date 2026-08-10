# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 14:26:47 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class LminC_ind_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if', 'low_spot_if']

        super(LminC_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)
    


    def on_bar(self, data):

        lltc_ind_r = -data['low_spot_if'].rolling(180, min_periods = 90).min()/(data['close_spot_if'])
        factor = lltc_ind_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        # factor[factor<-0.8] = 0
        return factor
