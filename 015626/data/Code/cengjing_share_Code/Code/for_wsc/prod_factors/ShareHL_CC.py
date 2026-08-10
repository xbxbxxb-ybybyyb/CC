# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 14:34:24 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class ShareHL_CC(FactorGenerator):
    def __init__(self):

        required_columns =['share']

        super(ShareHL_CC, self).__init__(
                                  required_columns=required_columns)
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    

    def on_bar(self, data):
        idx = data.index
        data = data.loc[~((idx.hour==9) & (idx.minute < 30))]
        data = data.sort_index()
        temp1 = data['share'].rolling(30, min_periods = 15).max()
        temp2 = data['share'].rolling(30, min_periods = 15).min()
        temp3 = temp1-temp2
        t_prcd2 = temp3.rolling(10, min_periods = 5).mean()
        factor = t_prcd2.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor
