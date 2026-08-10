# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 14:04:46 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

# demo
class hhll_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot', 'low_spot']

        super( hhll_ind_CC, self).__init__(
                                  required_columns=required_columns)


    def on_bar(self, data):

        temp = np.where((data['high_spot']>data['high_spot'].shift(1)) & (data['low_spot']>data['low_spot'].shift(1)), 4, np.where((data['high_spot']<data['high_spot'].shift(1)) & (data['low_spot']<data['low_spot'].shift(1)), 0, 1))
        temp = pd.Series(temp)
        temp.index = data['high_spot'].index
        vwtc_r = temp.rolling(45, min_periods =30).mean()
        factor = vwtc_r.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 2420)
        return factor