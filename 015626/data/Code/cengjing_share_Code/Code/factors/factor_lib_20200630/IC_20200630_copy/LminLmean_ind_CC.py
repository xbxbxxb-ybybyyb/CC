# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:15:32 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class LminLmean_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns =['low_spot']
        super(LminLmean_ind_CC, self).__init__(
                                  required_columns=required_columns)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, data):

        ctl_r = -data['low_spot'].rolling(50, min_periods =30).min()/data['low_spot'].rolling(30, min_periods =15).mean()
        factor = ctl_r.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor