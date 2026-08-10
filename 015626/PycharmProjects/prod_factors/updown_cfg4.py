# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 11:07:07 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


# demo
class updown_cfg4(FactorGenerator):
    def __init__(self):

        required_columns =['upclose', 'downclose', 'upvolume', 'downvolume']

        super(updown_cfg4, self).__init__(
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
        vwtc_r = ((data['upclose']/data['downclose'])/(data['upvolume']/data['downvolume'])).rolling(30, min_periods = 15).mean()
        factor = vwtc_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor
    