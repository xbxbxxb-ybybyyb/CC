# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 14:40:35 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class Absvc_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close', 'volume', 'recent_month_mask']
        super(Absvc_CC, self).__init__(
                                  required_columns=required_columns)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):

        temp1 = data['close'].diff()
        temp2 = np.abs(data['volume'] * temp1)
        hdl_ind_r = temp2.rolling(20, min_periods = 10).mean()
        factor = (hdl_ind_r[data['recent_month_mask']]).mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor