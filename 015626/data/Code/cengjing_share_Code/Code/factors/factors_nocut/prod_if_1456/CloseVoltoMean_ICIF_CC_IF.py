# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 19:12:21 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class CloseVoltoMean_ICIF_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot']

        super(CloseVoltoMean_ICIF_CC_IF, self).__init__(
                                  required_columns=required_columns)
        


    def on_bar(self, data):

        prstd3_r = data['close_spot'].rolling(30, min_periods =10).std()/data['close_spot'].rolling(30, min_periods =15).mean()
        prstd3_r[abs(prstd3_r)>100000] = np.nan
        prstd3_r = prstd3_r.rolling(15, min_periods = 2).mean()
        factor = prstd3_r.to_frame()

        factor.columns =  [self.__class__.__name__]
        factor = ts_rank(factor)
        # factor[factor>1] = 0
        # factor[factor<=-0.5] = 0
        return factor

