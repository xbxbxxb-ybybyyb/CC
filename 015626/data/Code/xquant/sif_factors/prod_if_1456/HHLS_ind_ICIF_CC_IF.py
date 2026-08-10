# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 15:06:14 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class HHLS_ind_ICIF_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot','recent_month_mask']

        super(HHLS_ind_ICIF_CC_IF, self).__init__(required_columns=required_columns)
    

    

    
    def on_bar(self, data):

        temp = data['high_spot'].rolling(50, min_periods = 15).max() - data['high_spot'].shift(50).rolling(50, min_periods = 7).max()
        factor = temp.to_frame()

        #factor = np.abs(factor)

        factor = rolling_norm(factor)
        # factor[factor<-1] = 0
        # factor[factor>1] = 0
        factor.columns = [self.__class__.__name__]
        return factor