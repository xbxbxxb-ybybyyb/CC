# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:00:17 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class SmaxSmean_CC(FactorGenerator):
    def __init__(self):
        required_columns =['share', 'recent_month_mask']
        super(SmaxSmean_CC, self).__init__(
                                  required_columns=required_columns)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, data):

        pd1_r = data['share'].rolling(30, min_periods = 5).mean() - data['share'].rolling(120, min_periods = 75).mean()
        factor = (pd1_r[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        factor[factor<=-0.5] = 0
        return factor


