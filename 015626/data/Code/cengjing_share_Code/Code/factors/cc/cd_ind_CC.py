# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 14:19:00 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
import numpy as np
from operators_cc import *


class cd_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns =['close_spot']
        
        super(cd_ind_CC, self).__init__(
                                  required_columns=required_columns)
       

    def on_bar(self, data):

        temp = data['close_spot'].rolling(60, min_periods = 2).mean().diff()
        factor = temp.to_frame()
        factor.columns =  [self.__class__.__name__]
        factor = rolling_norm(factor, 1000)
        factor[factor<0] = 0
        factor[factor>1] = 0
        return factor