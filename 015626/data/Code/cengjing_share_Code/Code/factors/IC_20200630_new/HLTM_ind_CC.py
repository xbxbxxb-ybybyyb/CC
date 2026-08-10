# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:09:56 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *


class HLTM_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'high_spot', 'low_spot']

        super(HLTM_ind_CC, self).__init__(
                                  required_columns=required_columns)
    def on_bar(self, data):

        temp1 = data['high_spot'].rolling(15, min_periods = 7).max()-data['close_spot']
        temp2 = data['close_spot']-data['low_spot'].rolling(15, min_periods = 7).min()
        temp = pd.Series(np.where(temp1>temp2, temp1, temp2))
        temp.index = temp1.index
        vwtc_r = (temp).rolling(30, min_periods = 15).mean()      
        factor = vwtc_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, 242*4)
        factor = ts_rank(factor)
        return factor