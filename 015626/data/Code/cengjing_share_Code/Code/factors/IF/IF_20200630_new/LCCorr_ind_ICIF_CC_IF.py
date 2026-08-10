# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 14:26:40 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class LCCorr_ind_ICIF_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'low_spot']

        super(LCCorr_ind_ICIF_CC_IF, self).__init__(
                                  required_columns=required_columns)


    def on_bar(self, data):

        high = data['low_spot']
        close = data['close_spot']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_chgpcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)
        factor = t_chgpcor2.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor.rolling(5, min_periods = 2).mean())
        factor = ts_rank(factor)
        return factor
