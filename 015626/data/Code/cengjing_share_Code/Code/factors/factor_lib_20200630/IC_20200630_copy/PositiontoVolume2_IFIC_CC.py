# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 10:45:34 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


# demo
class PositiontoVolume2_IFIC_CC(FactorGenerator):
    def __init__(self):
        
        required_columns =['volume_if', 'position_if', 'recent_month_mask']
        super(PositiontoVolume2_IFIC_CC, self).__init__(
                                  required_columns=required_columns)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):
        a = data['position_if']
        a[abs(a) < 1e-8] = np.nan
        temp = data['volume_if']/a
        hdl_ind_r = temp.rolling(20, min_periods = 15).mean()
        factor = (hdl_ind_r[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor
