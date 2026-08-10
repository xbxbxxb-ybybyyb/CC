# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:18:15 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class ClMaxClMin_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot']
 
        super(ClMaxClMin_ind_CC, self).__init__(
                                  required_columns=required_columns)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, data):

        m_vwap_ind_r = (data['close_spot']).rolling(60, min_periods = 30).max()/data['close_spot'].rolling(60, min_periods = 30).min()
        factor = m_vwap_ind_r.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor

