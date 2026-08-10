# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 14:10:10 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class GA_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'low_spot', 'open_spot', 'high_spot']

        super( GA_ind_CC, self).__init__(
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
        a = data['high_spot'].rolling(120, min_periods = 60).max()-data['open_spot'].shift(120)
        b = data['close_spot'] - data['low_spot'].rolling(120, min_periods = 60).min()
        c = (data['high_spot'].rolling(120, min_periods = 60).max()-data['low_spot'].rolling(120, min_periods = 60).min())*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = (a+b)/c
        factor = vwtc_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor

