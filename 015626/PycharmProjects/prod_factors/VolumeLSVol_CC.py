# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:15:27 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

# demo
class VolumeLSVol_CC(FactorGenerator):
    def __init__(self):

        required_columns =['volume']

        super(VolumeLSVol_CC, self).__init__(
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
        prstd2_r = -data['volume'].rolling(1800, min_periods = 900).std()/data['volume'].rolling(90, min_periods = 45).std()
        factor = prstd2_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor