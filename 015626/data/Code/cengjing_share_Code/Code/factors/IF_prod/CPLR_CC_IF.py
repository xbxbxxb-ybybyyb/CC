# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 11:10:24 2020

@author: appadmin
"""
from factor_generator import FactorGenerator
from operators_cc import *
import pandas as pd
import numpy as np

class CPLR_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if']
 
        super(CPLR_CC_IF, self).__init__(
                                  required_columns=required_columns)
        
    def on_bar(self, data):
        #LINEARREG_SLOPE(ts_max(close_spot, 40), 70)
        
        x = np.array(range(len(data['close_spot_if'])))
        temp = data['close_spot_if'].rolling(40, min_periods = 20).max()
        factor = pd.Series(rolling_linear_reg(x, temp, 75))
        factor.index = data['close_spot_if'].index
        
        factor = ts_rank(factor.to_frame(), 242*2)
        factor.columns = [self.__class__.__name__]
        #factor[factor<-0] = 0
        return factor