# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 13:29:06 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class SFCV_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close', 'volume']

        super(SFCV_CC, self).__init__(
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
        t_chgpcor1 = ((data['close'])*data['volume']).rolling(10, min_periods = 2).mean()/((data['close'])*data['volume']).rolling(90, min_periods = 30).mean()
        factor = t_chgpcor1.rolling(10,min_periods = 2).mean().to_frame()
        factor.index = data.index

        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        factor[factor<-1] = np.nan
        factor[factor>1] = np.nan
        return factor
