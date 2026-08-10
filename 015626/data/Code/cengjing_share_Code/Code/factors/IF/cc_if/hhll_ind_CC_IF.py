# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 16:48:03 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


# demo
class hhll_ind_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot_if', 'low_spot_if','recent_month_mask']

        super(hhll_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)



    def on_bar(self, data):

        temp = np.where((data['high_spot_if']>data['high_spot_if'].shift(1)) & (data['low_spot_if']>data['low_spot_if'].shift(1)), 4, np.where((data['high_spot_if']<data['high_spot_if'].shift(1)) & (data['low_spot_if']<data['low_spot_if'].shift(1)), 0, 1))
        temp = pd.Series(temp)
        temp.index = data['high_spot_if'].index
        vwtc_r = temp.rolling(120, min_periods =10).mean()
        factor = vwtc_r.to_frame()
        factor = np.abs(factor)
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        factor[factor<=-0.5] = 0
        return factor
