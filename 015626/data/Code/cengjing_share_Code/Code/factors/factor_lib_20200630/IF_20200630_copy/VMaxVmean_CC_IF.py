# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 16:06:43 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator import FactorGenerator

class VMaxVmean_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['vwap', 'recent_month_mask']
        super(VMaxVmean_CC_IF, self).__init__(required_columns=required_columns)

        
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):

        m_vwap_r = data['vwap'].rolling(60, min_periods = 30).max()/data['vwap'].rolling(60, min_periods = 30).min()
        factor = m_vwap_r[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor, 480)
        return factor
