# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 15:07:08 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class LCCorr_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'low_spot']

        super(LCCorr_ind_CC, self).__init__(
                                  required_columns=required_columns)

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
        # t_chgpcor = pd.concat([data['low_spot'], data['close_spot']], axis = 1)
        # t_chgpcor2 = t_chgpcor.rolling(60, min_periods = 30).corr(pairwise=True).unstack()
        # t_chgpcor2 = t_chgpcor2[('low_spot', 'close_spot')]
        # t_chgpcor2[t_chgpcor2 == np.inf] = 1

        high = data['low_spot']
        close = data['close_spot']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_chgpcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)

        factor = t_chgpcor2.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor