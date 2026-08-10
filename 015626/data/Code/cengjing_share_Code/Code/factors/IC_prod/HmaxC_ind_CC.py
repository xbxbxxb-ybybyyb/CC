# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 16:48:02 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HmaxC_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'high_spot']

        super(HmaxC_ind_CC, self).__init__(
                                  required_columns=required_columns)
        

    def on_bar(self, data):

        hmhm_r = -data['high_spot'].rolling(120, min_periods = 90).max()/data['close_spot']
        hmhm_r[abs(hmhm_r)>100000] = np.nan
        factor = hmhm_r.to_frame()
  
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 1000)
        factor[factor<0]=0
        return factor