# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 08:55:09 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class HDL_CC(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high']
        super(HDL_CC, self).__init__(required_columns=required_columns)
        
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
        
    def on_bar(self, data):
        idx = data.index
        data = data.loc[~(((idx.hour==9) & (idx.minute < 30)) | ((idx.hour==11) & (idx.minute == 30)))]
        data = data.sort_index()
        hdl_r = (data['high'].rolling(25, min_periods = 10).max())/(data['low'].rolling(25, min_periods = 10).min())
        factor = (hdl_r.rolling(10, min_periods = 2).mean()).to_frame()
        factor.columns = [self.__class__.__name__]
        factors = self.ts_rank(factor)
        factors[factors<=-0.5] = np.nan
        return factors