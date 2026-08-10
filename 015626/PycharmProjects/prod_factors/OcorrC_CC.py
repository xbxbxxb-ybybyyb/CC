# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:48:29 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


class OcorrC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['open', 'close']

        super(OcorrC_CC, self).__init__(
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
        t_occor = data.loc[:, ['open', 'close']]
        t_occor2 = t_occor.rolling(60, min_periods = 30).corr(pairwise=True).unstack()
        t_occor2 = t_occor2[('open', 'close')]
        t_occor2[t_occor2 == np.inf] = 1       
        factor = t_occor2.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor
