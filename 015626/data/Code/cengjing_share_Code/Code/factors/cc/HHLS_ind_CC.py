# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:07:05 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HHLS_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot']

        super(HHLS_ind_CC, self).__init__(required_columns=required_columns)

    
    def on_bar(self, data):

        temp = data['high_spot'].rolling(50, min_periods = 15).max() - data['high_spot'].shift(50).rolling(50, min_periods = 7).max()
        factor = temp.to_frame()
        factor = rolling_norm(factor)
        factor.columns = [self.__class__.__name__]
        return factor