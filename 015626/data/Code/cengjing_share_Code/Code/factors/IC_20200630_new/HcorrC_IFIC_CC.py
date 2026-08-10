# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 17:32:21 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HcorrC_IFIC_CC(FactorGenerator):
    def __init__(self):
        required_columns =['high_if', 'close_if', 'recent_month_mask']

        super(HcorrC_IFIC_CC, self).__init__(
                                  required_columns=required_columns)
        

    def on_bar(self, data):

        high = data['high_if']
        close = data['close_if']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_pcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)

        t_pcor2[abs(t_pcor2) > 1e8] = 0
        factor = t_pcor2[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor