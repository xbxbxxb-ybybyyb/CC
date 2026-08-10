# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:12:24 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class VwapLSVol_CC(FactorGenerator):
    def __init__(self):

        required_columns =['vwap', 'recent_month_mask']

        super(VwapLSVol_CC, self).__init__(
                                  required_columns=required_columns)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):

        prstd_r = -data['vwap'].rolling(1200, min_periods = 600).std()/data['vwap'].rolling(45, min_periods = 15).std()
        factor = (prstd_r[data['recent_month_mask']]).mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor