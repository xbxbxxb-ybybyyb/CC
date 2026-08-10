# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:18:41 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class CloseVoltoMean_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'recent_month_mask']

        super(CloseVoltoMean_ind_CC, self).__init__(
                                  required_columns=required_columns)

    
    def on_bar(self, data):

        prstd3_r = data['close_spot'].rolling(40, min_periods =5).std()/data['close_spot'].rolling(40, min_periods =15).mean()
        factor = prstd3_r.to_frame()

        factor.columns =  [self.__class__.__name__]
        factor = rolling_norm(factor, method = 'ts_rank')
        factor[factor<-0.2]=0
        return factor
