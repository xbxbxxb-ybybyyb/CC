# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 16:49:29 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from operators_cc import *

class Rev_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot']

        super(Rev_ind_CC, self).__init__(
                                  required_columns=required_columns)
    
    def on_bar(self, data):
        vwtc_r = data['close_spot']/data['close_spot'].shift(120)-1
        factor = vwtc_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, 4800)
        # factor[factor<-1] = np.nan
        # factor[factor>1] = np.nan
        return factor