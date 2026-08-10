# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 11:10:27 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class VwapLSVol_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['vwap_if', 'recent_month_mask']

        super(VwapLSVol_CC_IF, self).__init__(
                                  required_columns=required_columns)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):

        a = data['vwap_if'].rolling(45, min_periods = 15).std()
        a[abs(a) < 1e-8] = np.nan
        prstd_r = -data['vwap_if'].rolling(1200, min_periods = 600).std()/a
        factor = prstd_r[data['recent_month_mask']].mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor