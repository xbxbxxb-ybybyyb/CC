# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 14:19:05 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class RolTrendLS_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'low_spot', 'high_spot']

        super(RolTrendLS_ind_CC, self).__init__(
                                  required_columns=required_columns)
        


    def on_bar(self, data):
        a = (data['high_spot'].rolling(60, min_periods = 15).max() - data['low_spot'].rolling(60, min_periods = 15).min())
        a[abs(a)<1e-8] = np.nan
        ll = (data['close_spot'] - data['low_spot'].rolling(60, min_periods = 15).min()) / a
        a2 = ll.rolling(10, min_periods = 5).mean()
        a3 = a2.rolling(10, min_periods = 5).mean()
        vwtc_r = 3*a3-2*a2
        factor = vwtc_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor