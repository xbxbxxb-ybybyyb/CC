# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 17:09:17 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class HcorrC_ind_IFIC_CC(FactorGenerator):
    def __init__(self):
        
        required_columns =['close_spot_if', 'high_spot_if']
        
        super(HcorrC_ind_IFIC_CC, self).__init__(
                                  required_columns=required_columns)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, data):
        idx = data.index
        data = data.loc[~(((idx.hour==9) & (idx.minute < 30)) | ((idx.hour==11) & (idx.minute == 30)))]
        data = data.sort_index()
        # t_pcor = data.loc[:, ['high_spot_if', 'close_spot_if']]
        # t_pcor2 =  t_pcor.rolling(60, min_periods =30).corr(pairwise=True).unstack()
        # t_pcor2 = t_pcor2[('high_spot_if', 'close_spot_if')]

        high = data['high_spot_if']
        close = data['close_spot_if']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_pcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)

        t_pcor2[t_pcor2 == np.inf] = 0
        factor = t_pcor2.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor, 2420)
        return factor
