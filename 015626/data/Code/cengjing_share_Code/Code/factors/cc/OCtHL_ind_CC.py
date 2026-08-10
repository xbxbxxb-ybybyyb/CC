# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 14:14:51 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class OCtHL_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot', 'low_spot', 'close_spot', 'open_spot']

        super(OCtHL_ind_CC, self).__init__(
                                  required_columns=required_columns)

    def on_bar(self, data):
        temp1 = data['open_spot'] - data['close_spot']
        temp2 = data['high_spot'] - data['low_spot']
        temp2[abs(temp2)<1e-8] = np.nan
        t_pcor2 = -temp1/temp2
        t_pcor2[abs(t_pcor2) > 1e8] = 0
        t_pcor2 = t_pcor2.rolling(30, min_periods = 15).mean().rolling(5, min_periods = 2).mean()
        factor = t_pcor2.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor
    