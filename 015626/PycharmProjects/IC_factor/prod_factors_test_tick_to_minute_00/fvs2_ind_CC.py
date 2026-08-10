# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 14:42:11 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class fvs2_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'close']

        super(fvs2_ind_CC, self).__init__(
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
        # temp =pd.concat([data['close_spot'], data['close']], axis = 1)
        # temp.columns = ['s', 'f']
        # t_pcor2 = temp.rolling(45, min_periods = 30).corr(pairwise=True).unstack()
        # vwtc_r = t_pcor2[('s', 'f')]
        close_spot = data['close_spot']
        close = data['close']
        s = close_spot.rolling(45, min_periods=30).std()
        f = close.rolling(45, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        vwtc_r = close_spot.rolling(45, min_periods=30).cov(close) / (s * f)
        factor = (vwtc_r*np.sign(data['close_spot'] - data['close'])).to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        #factor[factor<=-0.5] = np.nan
        return factor