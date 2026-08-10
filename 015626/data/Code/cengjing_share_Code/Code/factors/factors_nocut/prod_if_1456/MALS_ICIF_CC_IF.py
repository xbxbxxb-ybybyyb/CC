# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 13:46:35 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class MALS_ICIF_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['low_spot']
        super(MALS_ICIF_CC_IF, self).__init__(required_columns=required_columns)
        

    

    
    def on_bar(self, data):

        temp = data['low_spot'].rolling(75, min_periods = 15).mean() - data['low_spot'].shift(15).rolling(60, min_periods = 7).mean()
        factor = temp.to_frame()
        factor = ts_rank(factor, 242*2)
        # factor[factor<-0.5] = 0
        factor.columns = [self.__class__.__name__]
        return factor