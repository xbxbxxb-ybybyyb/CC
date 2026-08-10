# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 14:16:10 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

# demo
class UOH_CC(FactorGenerator):
    def __init__(self):
        required_columns =['upopentohigh']
        super(UOH_CC, self).__init__(
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
        temp1 = data['upopentohigh'].rolling(30, min_periods = 15).mean().rolling(5, min_periods = 2).mean()
        t_pcorr = temp1
        factor = t_pcorr.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        factor[factor<-0.5]=np.nan
        return factor
