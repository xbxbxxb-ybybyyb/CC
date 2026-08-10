# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 18:52:13 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class fvs2_ind_IFIC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if', 'close_if']

        super(fvs2_ind_IFIC_CC, self).__init__(
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
        # temp =pd.concat([data['close_spot_if'], data['close_if']], axis = 1)
        # temp.columns = ['s', 'f']
        # t_pcor2 = temp.rolling(40, min_periods = 15).corr(pairwise=True).unstack()
        # vwtc_r = t_pcor2[('s', 'f')]
        close_spot = data['close_spot_if']
        close = data['close_if']
        s = close_spot.rolling(40, min_periods=15).std()
        f = close.rolling(40, min_periods=15).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        vwtc_r = close_spot.rolling(40, min_periods=15).cov(close) / (s * f)
        factor = (vwtc_r*np.sign(data['close_spot_if'] - data['close_if'])).to_frame()
        factor.index = data.index
        factor = np.abs(factor)
        factor.iloc[:, 0] = factor.iloc[:, 0].rolling(5, min_periods = 2).mean()
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        #factor[factor<=-0.7] = np.nan

        return factor

