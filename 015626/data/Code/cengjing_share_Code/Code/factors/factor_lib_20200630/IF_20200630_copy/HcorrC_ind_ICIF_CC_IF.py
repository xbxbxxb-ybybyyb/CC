# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 17:25:40 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class HcorrC_ind_ICIF_CC_IF(FactorGenerator):
    def __init__(self):
        
        required_columns =['close_spot', 'high_spot']
        
        super(HcorrC_ind_ICIF_CC_IF, self).__init__(
                                  required_columns=required_columns)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, data):
        high = data['high_spot']
        close = data['close_spot']
        s = high.rolling(45, min_periods=30).std()
        f = close.rolling(45, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_pcor2 = high.rolling(45, min_periods=30).cov(close) / (s * f)
        factor = t_pcor2.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = factor.rolling(30, min_periods = 7).mean()
        factor = self.ts_rank(factor)  
        return factor


