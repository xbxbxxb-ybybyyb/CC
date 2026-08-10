# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 14:08:02 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
# demo
class GA_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close', 'low', 'open', 'high']

        super( GA_CC, self).__init__(
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
        a = data['high'].rolling(120, min_periods = 60).max()-data['open'].shift(120)
        b = data['close'] - data['low'].rolling(120, min_periods = 60).min()
        c = (data['high'].rolling(120, min_periods = 60).max()-data['low'].rolling(120, min_periods = 60).min())*2
        vwtc_r = (a+b)/c
        factor = (vwtc_r.rolling(10, min_periods = 5).mean()).to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor