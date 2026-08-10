# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:50:31 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HLLSVol_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high', 'low', 'recent_month_mask']
 
        super(HLLSVol_CC, self).__init__(
                                  required_columns=required_columns)
    

    def on_bar(self, data):

        a = (data['high']/data['low']).rolling(240, min_periods =10).std()
        a[a<1e-10] = np.nan
        ocre3_r = (data['high']/data['low']).rolling(40, min_periods =10).std()/a
        factor = ocre3_r[data['recent_month_mask']].mean(axis = 1).to_frame()
 
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        factor[factor<0]=0
        return factor
    
