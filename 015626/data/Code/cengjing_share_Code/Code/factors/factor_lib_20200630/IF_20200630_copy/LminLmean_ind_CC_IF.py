# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 14:31:16 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator import FactorGenerator

class LminLmean_ind_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns =['low_spot_if']
        super(LminLmean_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):

        ctl_r = -data['low_spot_if'].rolling(45, min_periods =30).min()/data['low_spot_if'].rolling(25, min_periods =15).mean()
        factor = ctl_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor
