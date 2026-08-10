# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:54:19 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

# demo
class CLSH_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close', 'share', 'recent_month_mask']

        super(CLSH_CC, self).__init__(
                                  required_columns=required_columns)

    def on_bar(self, data):

        temp1 = pd.DataFrame(np.where(data['close'].diff()>0, 1, np.where(data['close'].diff()<0, -1, 0)))
        temp1.index = data['close'].index
        temp1.columns = data['close'].columns
        temp1 = (temp1[data['recent_month_mask']]).mean(axis = 1)
        temp2 = np.abs(((data['share'])[data['recent_month_mask']]).mean(axis = 1) * temp1)
        hdl_ind_r = temp2.rolling(30, min_periods = 15).mean()
        factor = hdl_ind_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor)

        return factor