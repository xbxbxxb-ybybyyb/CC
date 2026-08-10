# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 14:39:54 2020

@author: appadmin
"""

import pandas as pd
import bottleneck as bk
from factor_generator import FactorGenerator
import numpy as np



class td_ind_IFIC_CC(FactorGenerator):
    def __init__(self):
        required_columns = ['low_spot_if', 'high_spot_if']

        super(td_ind_IFIC_CC, self).__init__(
            required_columns=required_columns)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:, 0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def on_bar(self, data):
        idx = data.index
        data = data.loc[~(((idx.hour == 9) & (idx.minute < 30)) | ((idx.hour == 11) & (idx.minute == 30)))]
        data = data.sort_index()
        temp = data['low_spot_if'].rolling(10, min_periods=5).min() - data['low_spot_if'].rolling(120, min_periods=5).min() + \
               data['high_spot_if'].rolling(10, min_periods=5).max() - data['high_spot_if'].rolling(120, min_periods=5).max()
        temp.index = data.index
        factor = temp.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor)
        factor = self.ts_rank(factor)
        factor[factor <=-0.5] = np.nan
        factor[factor > 1] = np.nan

        return factor