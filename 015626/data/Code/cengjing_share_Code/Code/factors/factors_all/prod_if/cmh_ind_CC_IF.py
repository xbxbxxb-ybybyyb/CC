# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 16:15:39 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class cmh_ind_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns =['high_spot_if', 'close_spot_if', 'recent_month_mask']
        
        super(cmh_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)

    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):

        vwtc_r = (data['high_spot_if']-data['close_spot_if'].rolling(120, min_periods = 30).mean())
        factor = vwtc_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor, 2420)
        factor[factor<=-0.5] = 0
        return factor
